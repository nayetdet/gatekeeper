import aiohttp
from contextlib import suppress
from loguru import logger
from typing import List, Dict, Any, Optional
from yarl import URL
from gatekeeper.config import config
from gatekeeper.enums.product_type import ProductType
from gatekeeper.models.product import Product
from gatekeeper.repositories.product_repository import ProductRepository

class DiscoveryService:
    __BASE_STORE_URL: URL = URL("https://store.epicgames.com")
    __BASE_STORE_PROMOTIONS_URL: URL = URL("https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions")

    @classmethod
    def get_store_url(cls) -> URL:
        locale: str = config.EPIC_GAMES_LOCALE
        return cls.__BASE_STORE_URL / locale

    @classmethod
    def get_store_promotions_url(cls) -> URL:
        locale: str = config.EPIC_GAMES_LOCALE
        country: str = config.EPIC_GAMES_COUNTRY
        return cls.__BASE_STORE_PROMOTIONS_URL.with_query(
            {
                "locale": locale,
                "country": country,
                "allowCountries": [
                    country
                ]
            }
        )

    @classmethod
    def get_store_product_url(cls, slug: str, ptype: ProductType) -> URL:
        return cls.get_store_url() / ptype.value / slug

    @classmethod
    async def get_free_products(cls) -> List[URL]:
        logger.info("Fetching free products from Epic Games promotions API")
        urls: List[URL] = []
        async with aiohttp.ClientSession() as session:
            async with session.get(cls.get_store_promotions_url()) as response:
                response.raise_for_status()
                data: Dict[str, Any] = await response.json()

        for element in data["data"]["Catalog"]["searchStore"]["elements"]:
            try: slug, ptype = element["offerMappings"][0]["pageSlug"], ProductType.PRODUCT
            except (IndexError, KeyError, TypeError):
                slug, ptype = element.get("productSlug"), ProductType.BUNDLE
                if not slug:
                    continue

            with suppress(IndexError, KeyError, TypeError):
                for offer in element["promotions"]["promotionalOffers"][0]["promotionalOffers"]:
                    if offer["discountSetting"]["discountPercentage"] == 0:
                        urls.append(cls.get_store_product_url(slug, ptype))

        logger.info("Total free products found: {}", len(urls))
        return urls

    @classmethod
    async def get_unclaimed_free_products(cls) -> List[URL]:
        unclaimed_urls: List[URL] = []
        for url in await cls.get_free_products():
            product: Optional[Product] = await ProductRepository.get_by_url(str(url))
            if not product:
                logger.info("Unclaimed free product found: {}", url)
                unclaimed_urls.append(url)
            else: logger.info("Already claimed free product found: {}", url)

        logger.info("Total free unclaimed products found: {}", len(unclaimed_urls))
        return unclaimed_urls
