from yarl import URL
from gatekeeper.config import config
from gatekeeper.enums.product_path_type import ProductPathType

class StoreUrlFactory:
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
    def get_store_product_url(cls, slug: str, path_type: ProductPathType) -> URL:
        return cls.get_store_url() / path_type.value / slug
