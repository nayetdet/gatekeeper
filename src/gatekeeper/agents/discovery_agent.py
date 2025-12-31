import aiohttp
from contextlib import suppress
from loguru import logger
from typing import List, Dict, Any, Optional
from playwright.async_api import Page, Locator
from yarl import URL
from gatekeeper.config import config
from gatekeeper.decorators.retry_decorator import retry
from gatekeeper.enums.product_path_type import ProductPathType
from gatekeeper.models.product import Product
from gatekeeper.repositories.product_repository import ProductRepository

class DiscoveryAgent:
    __BASE_STORE_URL: URL = URL("https://store.epicgames.com")
    __BASE_STORE_PROMOTIONS_URL: URL = URL("https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions")

    def __init__(self, page: Page) -> None:
        self.__page: Page = page

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
    def get_store_product_url(cls, slug: str, path_type: ProductPathType) -> URL:
        return cls.get_store_url() / path_type.value / slug

    async def get_free_products(self) -> List[URL]:
        logger.info("Fetching free products from Epic Games promotions API")
        urls: List[URL] = []
        async with aiohttp.ClientSession() as session:
            async with session.get(self.get_store_promotions_url()) as response:
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
                    path_type: ProductPathType = await self.__get_product_path_type(slug)
                    urls.append(self.get_store_product_url(slug, path_type))

        logger.info("Total free products found: {}", len(urls))
        return urls

    async def get_unclaimed_free_products(self) -> List[URL]:
        unclaimed_urls: List[URL] = []
        for url in await self.get_free_products():
            product: Optional[Product] = await ProductRepository.get_by_url(str(url))
            if not product:
                logger.info("Unclaimed free product found: {}", url)
                unclaimed_urls.append(url)
            else: logger.info("Already claimed free product found: {}", url)

        logger.info("Total free unclaimed products found: {}", len(unclaimed_urls))
        return unclaimed_urls

    @retry(max_attempts=3, wait=5)
    async def __get_product_path_type(self, slug: str) -> ProductPathType:
        for ptype in ProductPathType:
            await self.__page.goto(str(self.get_store_product_url(slug, ptype)), wait_until="networkidle")
            error_view: Locator = self.__page.locator("//div[@data-component='ErrorView']")
            error_box: Locator = self.__page.locator("//div[@class='error-box']")
            if await error_view.count() == 0 and await error_box.count() == 0:
                return ptype
        raise LookupError(f"Product not found: {slug}")
