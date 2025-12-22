import aiohttp
from typing import List, Dict, Any, Optional
from yarl import URL

class EpicGamesUtils:
    BASE_STORE_URL: str = "https://store.epicgames.com/pt-BR/p/"
    STORE_PROMOTIONS_URL: str = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=pt-BR&country=BR&allowCountries=BR"

    @classmethod
    async def get_free_games(cls) -> List[str]:
        results: List[str] = []
        async with aiohttp.ClientSession() as session:
            async with session.get(cls.STORE_PROMOTIONS_URL) as response:
                response.raise_for_status()
                data: Dict[str, Any] = await response.json()

        for element in data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", []):
            offer_mappings: Optional[List[Dict[str, Any]]] = element.get("offerMappings", [])
            slug: Optional[str] = offer_mappings[0].get("pageSlug") if offer_mappings and isinstance(offer_mappings[0], dict) else element.get("productSlug")
            if slug is None:
                continue

            game_url: str = str(URL(cls.BASE_STORE_URL) / slug)
            discount_price: float = float(element.get("price", {}).get("totalPrice", {}).get("discountPrice", -1))
            if discount_price == 0:
                results.append(game_url)

        return results
