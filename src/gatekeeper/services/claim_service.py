from typing import List
from browserforge.fingerprints import Screen
from camoufox import AsyncCamoufox
from loguru import logger
from playwright.async_api import Page, ViewportSize
from yarl import URL
from gatekeeper.agents.auth_agent import AuthAgent
from gatekeeper.agents.hcaptcha_agent import HCaptchaAgent
from gatekeeper.agents.claim_agent import ClaimAgent
from gatekeeper.config import config
from gatekeeper.services.discovery_service import DiscoveryService

class ClaimService:
    @staticmethod
    async def claim_products() -> None:
        urls: List[URL] = await DiscoveryService.get_unclaimed_free_products()
        if not urls:
            logger.info("No unclaimed products found, skipping")
            return

        async with AsyncCamoufox(
            persistent_context=True,
            user_data_dir=config.BROWSER_PROFILE_PATH,
            record_video_dir=config.RECORDS_PATH,
            record_video_size=ViewportSize(width=1920, height=1080),
            screen=Screen(max_width=1920, max_height=1080, min_height=1080, min_width=1920),
            headless=True,
            humanize=1
        ) as browser:
            page: Page = browser.pages[0] if browser.pages else await browser.new_page()
            async with HCaptchaAgent(page) as hcaptcha_agent:
                auth_agent: AuthAgent = AuthAgent(page)
                claim_agent: ClaimAgent = ClaimAgent(page)
                for index, url in enumerate(urls, start=1):
                    logger.info("Processing product {}/{}: {}", index, len(urls), url)
                    await auth_agent.login_if_needed(hcaptcha_agent, redirect_url=url)
                    await claim_agent.claim_product(hcaptcha_agent, url=url)
