from pathlib import Path
from typing import Literal, Optional, Self
from hcaptcha_challenger import AgentConfig, FastShotModelType, SCoTModelType
from pydantic import SecretStr, model_validator

class Config(AgentConfig):
    # Browser
    BROWSER_HEADLESS: bool | Literal["virtual"] = True
    BROWSER_SCREEN_WIDTH: int = 1920
    BROWSER_SCREEN_HEIGHT: int = 1080

    # Epic Games
    EPIC_GAMES_EMAIL: SecretStr
    EPIC_GAMES_PASSWORD: SecretStr
    EPIC_GAMES_LOCALE: str
    EPIC_GAMES_COUNTRY: str

    # Agent
    MODEL: str = "gemini-2.5-flash"
    CHALLENGE_CLASSIFIER_MODEL: FastShotModelType = MODEL
    IMAGE_CLASSIFIER_MODEL: SCoTModelType = MODEL
    SPATIAL_POINT_REASONER_MODEL: SCoTModelType = MODEL
    SPATIAL_PATH_REASONER_MODEL: SCoTModelType = MODEL

    # Telegram Bot
    TELEGRAM_BOT_ENABLED: bool = True
    TELEGRAM_BOT_TOKEN: Optional[SecretStr] = None
    TELEGRAM_BOT_CHAT_ID: Optional[SecretStr] = None

    # Paths
    ROOT_PATH: Path = Path(__file__).resolve().parents[2]
    DATA_PATH: Path = ROOT_PATH / "data"

    DATABASE_PATH: Path = DATA_PATH / "database.sqlite"
    BROWSER_PROFILE_PATH: Path = DATA_PATH / "browser_profile"
    LOGS_PATH: Path = DATA_PATH / "logs"
    HCAPTCHA_PATH: Path = DATA_PATH / "hcaptcha"
    HTML_PATH: Path = DATA_PATH / "html"
    SCREENSHOTS_PATH: Path = DATA_PATH / "screenshots"
    RECORDS_PATH: Path = DATA_PATH / "records"

    cache_dir: Path = HCAPTCHA_PATH / ".cache"
    challenge_dir: Path = HCAPTCHA_PATH / ".challenge"
    captcha_response_dir: Path = HCAPTCHA_PATH / ".captcha"

    @model_validator(mode="after")
    def validate_telegram_bot(self) -> Self:
        if not self.TELEGRAM_BOT_ENABLED:
            return self
        for name in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_CHAT_ID"):
            if not getattr(self, name):
                raise ValueError(f"{name} must be configured when TELEGRAM_BOT_TOKEN is true")
        return self

config: Config = Config()
