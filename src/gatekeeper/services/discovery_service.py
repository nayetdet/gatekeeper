import aiohttp
from loguru import logger
from typing import List, Dict, Any, Optional
from yarl import URL
from gatekeeper.config import config
from gatekeeper.models.game import Game
from gatekeeper.repositories.game_repository import GameRepository

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
    def get_store_product_url(cls, product_slug: str) -> URL:
        return cls.get_store_url() / "p" / product_slug

    @classmethod
    async def get_free_games(cls) -> List[URL]:
        logger.info("Fetching free games from Epic Games promotions API")
        urls: List[URL] = []
        async with aiohttp.ClientSession() as session:
            async with session.get(cls.get_store_promotions_url()) as response:
                response.raise_for_status()
                data: Dict[str, Any] = await response.json()

        for element in data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", []):
            offer_mappings: Optional[List[Dict[str, Any]]] = element.get("offerMappings", [])
            slug: Optional[str] = offer_mappings[0].get("pageSlug") if offer_mappings and isinstance(offer_mappings[0], dict) else element.get("productSlug")
            if not slug or slug == "[]":
                continue

            discount_price: float = float(element.get("price", {}).get("totalPrice", {}).get("discountPrice", -1))
            if discount_price == 0:
                urls.append(cls.get_store_product_url(slug))

        logger.info("Total free games found: {}", len(urls))
        return urls

    @classmethod
    async def get_unclaimed_free_games(cls) -> List[URL]:
        unclaimed_urls: List[URL] = []
        for url in await cls.get_free_games():
            game: Optional[Game] = await GameRepository.get_by_url(str(url))
            if not game:
                logger.info("Unclaimed free game found: {}", url)
                unclaimed_urls.append(url)
            else: logger.info("Already claimed free game found: {}", url)

        logger.info("Total free unclaimed games found: {}", len(unclaimed_urls))
        return unclaimed_urls
