from typing import List
from loguru import logger
from playwright.async_api import Page
from yarl import URL
from gatekeeper.agents.auth_agent import AuthAgent
from gatekeeper.agents.hcaptcha_agent import HCaptchaAgent
from gatekeeper.agents.claim_agent import ClaimAgent
from gatekeeper.agents.discovery_agent import DiscoveryAgent
from gatekeeper.factories.browser.browser_factory import BrowserFactory
from gatekeeper.mappers.product_mapper import ProductMapper
from gatekeeper.repositories.product_repository import ProductRepository
from gatekeeper.schemas.product_schema import ProductSchema
from gatekeeper.services.discovery_service import DiscoveryService

class ClaimService:
    @classmethod
    async def claim_products(cls) -> None:
        products: List[ProductSchema] = await DiscoveryService.get_unclaimed_free_products()
        if not products:
            logger.info("No unclaimed products found, skipping")
            return

        async with BrowserFactory.build_browser() as browser:
            page: Page = browser.pages[0] if browser.pages else await browser.new_page()
            async with HCaptchaAgent(page) as hcaptcha_agent:
                auth_agent: AuthAgent = AuthAgent(page)
                await auth_agent.login_if_needed(hcaptcha_agent)

                claim_agent: ClaimAgent = ClaimAgent(page)
                discovery_agent: DiscoveryAgent = DiscoveryAgent(page)
                for index, product in enumerate(products, start=1):
                    try:
                        logger.info("Processing product {}/{}: {}", index, len(products), product)
                        product_url: URL = await discovery_agent.get_product_url(product)
                        await claim_agent.claim_product(hcaptcha_agent, url=product_url)
                    except Exception as e:
                        logger.error("Failed to claim product ({}/{}): {} - {}", index, len(products), product, e)
                        continue

                    logger.success("Product claim completed, saving to database (url={})", product_url)
                    await ProductRepository.create(ProductMapper.to_model(product))
