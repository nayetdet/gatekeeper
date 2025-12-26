import asyncio
from typing import List
from camoufox import AsyncCamoufox
from loguru import logger
from playwright.async_api import Page
from yarl import URL
from gatekeeper.agents.session_agent import SessionAgent
from gatekeeper.config import config
from gatekeeper.services.discovery_service import DiscoveryService

class ClaimService:
    @staticmethod
    async def claim_games(max_retries: int) -> None:
        logger.info("Claim started")
        urls: List[URL] = await DiscoveryService.get_unclaimed_free_games()
        if not urls:
            logger.info("Claim finished: no unclaimed games found")
            return

        async with AsyncCamoufox(persistent_context=True, user_data_dir=config.Paths.CONFIG, humanize=1, headless=False) as browser:
            page: Page = browser.pages[0] if browser.pages else await browser.new_page()
            async with SessionAgent(page=page) as session_agent:
                for index, url in enumerate(urls, start=1):
                    logger.info("Processing game {}/{}: {}", index, len(urls), url)
                    for attempt in range(1, max_retries + 1):
                        try:
                            logger.info("Attempt {}/{} for {}", attempt, max_retries, url)
                            await session_agent.claim_game(url)
                            await asyncio.sleep(30)
                            break
                        except Exception as e:
                            logger.exception("Error claiming game {} (attempt {}/{} | error={})", url, attempt, max_retries, e)
                    else: logger.error("Failed to claim {} after {} attempts", url, max_retries)

        logger.info("Claim finished")
