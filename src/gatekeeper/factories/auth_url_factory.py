from yarl import URL
from gatekeeper.config import config

class AuthUrlFactory:
    __BASE_AUTH_URL: URL = URL("https://www.epicgames.com/account/personal")

    @classmethod
    def get_auth_url(cls) -> URL:
        lang: str = config.EPIC_GAMES_LOCALE
        return cls.__BASE_AUTH_URL.with_query(
            {
                "lang": lang
            }
        )

    @classmethod
    def get_invalidated_auth_url(cls) -> URL:
        return cls.get_auth_url().update_query(
            {
                "productName": "egs",
                "sessionInvalidated": "true"
            }
        )
