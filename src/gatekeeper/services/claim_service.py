from typing import List
from loguru import logger
from yarl import URL
from gatekeeper.agents.auth_agent import AuthAgent
from gatekeeper.agents.claim_agent import ClaimAgent
from gatekeeper.agents.discovery_agent import DiscoveryAgent
from gatekeeper.contexts.browser_context import BrowserContext
from gatekeeper.contexts.hcaptcha_context import HCaptchaContext
from gatekeeper.mappers.product_mapper import ProductMapper
from gatekeeper.repositories.product_repository import ProductRepository
from gatekeeper.schemas.product_claim_summary_schema import ProductClaimSummarySchema
from gatekeeper.schemas.product_schema import ProductSchema
from gatekeeper.services.discovery_service import DiscoveryService

class ClaimService:
    @classmethod
    async def claim_products(cls, summary: ProductClaimSummarySchema) -> None:
        products: List[ProductSchema] = await DiscoveryService.get_unclaimed_free_products()
        if not products:
            summary.was_skipped = True
            logger.info("No unclaimed products found, skipping")
            return

        async with BrowserContext.get_page() as page, HCaptchaContext.get_challenger(page) as hcaptcha_challenger:
            auth_agent: AuthAgent = AuthAgent(page)
            claim_agent: ClaimAgent = ClaimAgent(page)
            discovery_agent: DiscoveryAgent = DiscoveryAgent(page)

            await auth_agent.login_if_needed(hcaptcha_challenger)
            for index, product in enumerate(products, start=1):
                summary.total += 1
                try:
                    logger.info("Processing product {}/{}: {}", index, len(products), product)
                    product_url: URL = await discovery_agent.get_product_url(product)
                    await claim_agent.claim_product(hcaptcha_challenger, url=product_url)
                except Exception as e:
                    summary.failure += 1
                    logger.error("Failed to claim product ({}/{}): {} - {}", index, len(products), product, e)
                    continue

                summary.success += 1
                logger.success("Product claim completed, saving to database (url={})", product_url)
                await ProductRepository.create(ProductMapper.to_model(product))
