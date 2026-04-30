from contextlib import asynccontextmanager
from typing import AsyncIterator
from browserforge.fingerprints import Screen
from camoufox import AsyncCamoufox
from playwright.async_api import Page, ViewportSize
from gatekeeper.config import config
from gatekeeper.utils.file_utils import FileUtils
from gatekeeper.utils.playwright_snapshot_utils import PlaywrightSnapshotUtils

class BrowserContext:
    @staticmethod
    @asynccontextmanager
    async def get_page() -> AsyncIterator[Page]:
        async with AsyncCamoufox(
            os=("windows",),
            persistent_context=True,
            user_data_dir=config.BROWSER_PROFILE_PATH,
            record_video_dir=FileUtils.get_directory_path(config.RECORDS_PATH),
            record_video_size=ViewportSize(
                width=config.BROWSER_SCREEN_WIDTH,
                height=config.BROWSER_SCREEN_HEIGHT
            ),
            screen=Screen(
                min_width=config.BROWSER_SCREEN_WIDTH,
                min_height=config.BROWSER_SCREEN_HEIGHT,
                max_width=config.BROWSER_SCREEN_WIDTH,
                max_height=config.BROWSER_SCREEN_HEIGHT
            ),
            slow_mo=500,
            headless=config.BROWSER_HEADLESS,
            humanize=True,
            disable_coop=True,
            i_know_what_im_doing=True
        ) as browser:
            page: Page = browser.pages[0] if browser.pages else await browser.new_page()
            try: yield page
            except Exception:
                await PlaywrightSnapshotUtils.save_snapshot(page)
                raise
