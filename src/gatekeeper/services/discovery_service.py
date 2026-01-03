import aiohttp
from contextlib import suppress
from typing import List, Dict, Any, Optional
from loguru import logger
from gatekeeper.decorators.retry_decorator import retry
from gatekeeper.factories.store_url_factory import StoreUrlFactory
from gatekeeper.mappers.product_mapper import ProductMapper
from gatekeeper.models import Product
from gatekeeper.repositories.product_repository import ProductRepository
from gatekeeper.schemas.product_schema import ProductSchema

class DiscoveryService:
    @staticmethod
    @retry(max_attempts=3, wait=5)
    async def get_free_products() -> List[ProductSchema]:
        products: List[ProductSchema] = []
        logger.info("Fetching free products from Epic Games promotions API")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=StoreUrlFactory.get_store_promotions_url(),
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                response.raise_for_status()
                data: Dict[str, Any] = await response.json()

        for element in data["data"]["Catalog"]["searchStore"]["elements"]:
            try: slug = element["offerMappings"][0]["pageSlug"]
            except (IndexError, KeyError, TypeError):
                slug = element.get("productSlug")
                if not slug or slug == "[]":
                    continue

            with suppress(IndexError, KeyError, TypeError):
                offers: List[Dict[str, Any]] = element["promotions"]["promotionalOffers"][0]["promotionalOffers"]
                if any(offer["discountSetting"]["discountPercentage"] == 0 for offer in offers):
                    products.append(ProductMapper.to_schema(
                        offer_id=element["id"],
                        namespace=element["namespace"],
                        slug=slug
                    ))

        logger.info("Total free products found: {}", len(products))
        return products

    @classmethod
    async def get_unclaimed_free_products(cls) -> List[ProductSchema]:
        unclaimed_products: List[ProductSchema] = []
        for product in await cls.get_free_products():
            product_model: Optional[Product] = await ProductRepository.get_by_offer_id_and_namespace(product.offer_id, product.namespace)
            if not product_model:
                logger.info("Unclaimed free product found: {}", product)
                unclaimed_products.append(product)
            else: logger.info("Already claimed free product found: {}", product)

        logger.info("Total free unclaimed products found: {}", len(unclaimed_products))
        return unclaimed_products
