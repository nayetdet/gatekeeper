import asyncio
from typing import List
from camoufox import AsyncCamoufox
from loguru import logger
from playwright.async_api import Page
from yarl import URL
from gatekeeper.config import config
from gatekeeper.services.session_service import SessionService
from gatekeeper.services.discovery_service import DiscoveryService

async def claim_games_task(max_retries: int = 5) -> None:
    logger.info("Task cycle started")
    discovery_service: DiscoveryService = DiscoveryService(locale=config.EpicGames.LOCALE, country=config.EpicGames.COUNTRY)
    urls: List[URL] = await discovery_service.get_unclaimed_free_games()
    if not urls:
        logger.info("Task cycle finished: no unclaimed games found")
        return

    async with AsyncCamoufox(persistent_context=True, user_data_dir=config.Paths.CONFIG, humanize=1, headless=True) as browser:
        page: Page = browser.pages[0] if browser.pages else await browser.new_page()
        session_service: SessionService = SessionService(page=page, locale=config.EpicGames.LOCALE)
        for index, url in enumerate(urls):
            logger.info("Processing game {}/{}: {}", index, len(urls), url)
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info("Attempt {}/{} for {}", attempt, max_retries, url)
                    await session_service.claim_game(url)
                    await asyncio.sleep(30)
                    break
                except Exception as e:
                    logger.exception("Error claiming game {} (attempt {}/{} | error={})", url, attempt, max_retries, e)
            else: logger.error("Failed to claim {} after {} attempts", url, max_retries)

    logger.info("Task cycle finished")
