import asyncio
import logging
from typing import List
from camoufox import AsyncCamoufox
from playwright.async_api import Page
from yarl import URL
from gatekeeper.config import config
from gatekeeper.services.session_service import SessionService
from gatekeeper.services.discovery_service import DiscoveryService

async def claim_games(max_retries: int = 3) -> None:
    discovery_service: DiscoveryService = DiscoveryService(locale=config.EpicGames.LOCALE, country=config.EpicGames.COUNTRY)
    urls: List[URL] = await discovery_service.get_unclaimed_free_games()
    if not urls:
        return

    async with AsyncCamoufox(persistent_context=True, user_data_dir=config.Paths.CONFIG, humanize=1, headless=True) as browser:
        page: Page = browser.pages[0] if browser.pages else await browser.new_page()
        session_service: SessionService = SessionService(page=page, locale=config.EpicGames.LOCALE)

        tmp_urls: List[URL] = urls.copy()
        while tmp_urls:
            url: URL = tmp_urls[0]
            for _ in range(max_retries):
                try: await session_service.claim_game(url)
                except Exception as e:
                    logging.error(f"Error claiming game {url}: {e}")
                    continue

                tmp_urls.pop(0)
                await asyncio.sleep(30)
