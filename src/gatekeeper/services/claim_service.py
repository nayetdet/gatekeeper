from typing import List
from camoufox import AsyncCamoufox
from loguru import logger
from playwright.async_api import Page
from yarl import URL
from gatekeeper.agents.auth_agent import AuthAgent
from gatekeeper.agents.captcha_agent import CaptchaAgent
from gatekeeper.agents.claim_agent import ClaimAgent
from gatekeeper.config import config
from gatekeeper.services.discovery_service import DiscoveryService

class ClaimService:
    @classmethod
    async def claim_games(cls) -> None:
        urls: List[URL] = await DiscoveryService.get_unclaimed_free_games()
        if not urls:
            logger.info("No unclaimed games found, skipping")
            return

        async with AsyncCamoufox(persistent_context=True, user_data_dir=config.BROWSER_PROFILE_PATH, humanize=0.2, headless=True) as browser:
            page: Page = browser.pages[0] if browser.pages else await browser.new_page()
            async with CaptchaAgent(page) as captcha_agent:
                auth_agent: AuthAgent = AuthAgent(page)
                claim_agent: ClaimAgent = ClaimAgent(page)
                for index, url in enumerate(urls, start=1):
                    logger.info("Processing game {}/{}: {}", index, len(urls), url)
                    await auth_agent.login_if_needed(captcha_agent=captcha_agent, redirect_url=url)
                    await claim_agent.claim_game(captcha_agent=captcha_agent, url=url)
