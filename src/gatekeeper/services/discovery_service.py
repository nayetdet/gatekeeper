import aiohttp
from typing import List, Dict, Any, Optional
from yarl import URL
from gatekeeper.models.game import Game
from gatekeeper.repositories.game_repository import GameRepository

class DiscoveryService:
    BASE_STORE_URL: URL = URL("https://store.epicgames.com")
    BASE_STORE_PROMOTIONS_URL: URL = URL("https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions")

    def __init__(self, locale: str, country: str) -> None:
        self.__locale: str = locale
        self.__country: str = country

    def get_promotions_url(self) -> URL:
        return self.BASE_STORE_PROMOTIONS_URL.with_query(
            {
                "locale": self.__locale,
                "country": self.__country,
                "allowCountries": [
                    self.__country
                ]
            }
        )

    def get_game_url(self, slug: str) -> URL:
        return self.BASE_STORE_URL / self.__locale / "p" / slug

    async def get_free_games(self) -> List[URL]:
        urls: List[URL] = []
        async with aiohttp.ClientSession() as session:
            async with session.get(self.get_promotions_url()) as response:
                response.raise_for_status()
                data: Dict[str, Any] = await response.json()

        for element in data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", []):
            offer_mappings: Optional[List[Dict[str, Any]]] = element.get("offerMappings", [])
            slug: Optional[str] = offer_mappings[0].get("pageSlug") if offer_mappings and isinstance(offer_mappings[0], dict) else element.get("productSlug")
            if not slug or slug == "[]":
                continue

            discount_price: float = float(element.get("price", {}).get("totalPrice", {}).get("discountPrice", -1))
            if discount_price == 0:
                urls.append(self.get_game_url(slug))
        return urls

    async def get_unclaimed_free_games(self) -> List[URL]:
        unclaimed_urls: List[URL] = []
        for url in await self.get_free_games():
            game: Optional[Game] = await GameRepository.get_by_url(str(url))
            if not game:
                unclaimed_urls.append(url)
        return unclaimed_urls
