import requests
from typing import List, Dict, Any, Optional

def free_games_urls():
    results: List[str] = []
    response = requests.get("https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=pt-BR&country=BR&allowCountries=BR")
    response.raise_for_status()
    for element in response.json().get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", []):
        offer_mappings: Optional[List[Dict[str, Any]]] = element.get("offerMappings", [])
        slug: Optional[str] = offer_mappings[0].get("pageSlug") if offer_mappings and isinstance(offer_mappings[0], dict) else element.get("productSlug")
        if slug is None:
            continue

        url = f"https://store.epicgames.com/pt-BR/p/{slug}"
        discount_price: float = float(element.get("price", {}).get("totalPrice", {}).get("discountPrice", -1))
        if discount_price == 0:
            results.append(url)
    return results

print(free_games_urls())
