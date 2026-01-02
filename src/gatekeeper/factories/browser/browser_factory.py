from contextlib import asynccontextmanager
from typing import Union, AsyncIterator
from browserforge.fingerprints import Screen
from camoufox import AsyncCamoufox
from playwright.async_api import ViewportSize, Browser, BrowserContext
from gatekeeper.config import config

class BrowserFactory:
    @staticmethod
    @asynccontextmanager
    async def build_browser() -> AsyncIterator[Union[Browser, BrowserContext]]:
        async with AsyncCamoufox(
            persistent_context=True,
            user_data_dir=config.BROWSER_PROFILE_PATH,
            record_video_dir=config.RECORDS_PATH,
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
            yield browser
