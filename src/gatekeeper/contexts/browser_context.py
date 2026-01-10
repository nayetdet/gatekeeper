from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator
from browserforge.fingerprints import Screen
from camoufox import AsyncCamoufox
from playwright.async_api import ViewportSize, Page
from gatekeeper.config import config

class BrowserContext:
    @staticmethod
    @asynccontextmanager
    async def get_page() -> AsyncIterator[Page]:
        async with AsyncCamoufox(
            os=("windows",),
            persistent_context=True,
            user_data_dir=config.BROWSER_PROFILE_PATH,
            record_video_dir=config.RECORDS_PATH / f"{datetime.now():%Y%m%dT%H%M%S}",
            record_video_size=ViewportSize(
                width=config.SCREEN_WIDTH,
                height=config.SCREEN_HEIGHT
            ),
            screen=Screen(
                min_width=config.SCREEN_WIDTH,
                min_height=config.SCREEN_HEIGHT,
                max_width=config.SCREEN_WIDTH,
                max_height=config.SCREEN_HEIGHT
            ),
            headless=True,
            humanize=1
        ) as browser:
            yield browser.pages[0] if browser.pages else await browser.new_page()
