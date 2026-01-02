import os
from pathlib import Path
from typing import Any, Optional
from hcaptcha_challenger import AgentConfig, FastShotModelType, SCoTModelType
from pydantic import Field, field_validator, SecretStr
from pydantic_core.core_schema import FieldValidationInfo

class Config(AgentConfig):
    # General
    SCREEN_WIDTH: int = 1366
    SCREEN_HEIGHT: int = 768
    CRONTAB: Optional[str] = Field(default_factory=lambda: os.getenv("CRONTAB"))

    # Epic Games
    EPIC_GAMES_EMAIL: SecretStr = Field(default_factory=lambda: os.getenv("EPIC_GAMES_EMAIL"))
    EPIC_GAMES_PASSWORD: SecretStr = Field(default_factory=lambda: os.getenv("EPIC_GAMES_PASSWORD"))
    EPIC_GAMES_LOCALE: str = Field(default_factory=lambda: os.getenv("EPIC_GAMES_LOCALE"))
    EPIC_GAMES_COUNTRY: str = Field(default_factory=lambda: os.getenv("EPIC_GAMES_COUNTRY"))

    # Models
    MODEL: str = "gemini-2.5-flash"
    CHALLENGE_CLASSIFIER_MODEL: FastShotModelType = MODEL
    IMAGE_CLASSIFIER_MODEL: SCoTModelType = MODEL
    SPATIAL_POINT_REASONER_MODEL: SCoTModelType = MODEL
    SPATIAL_PATH_REASONER_MODEL: SCoTModelType = MODEL

    # Paths
    ROOT_PATH: Path = Path(__file__).resolve().parents[2]
    DATA_PATH: Path = ROOT_PATH / "data"

    DATABASE_PATH: Path = DATA_PATH / "database.sqlite"
    BROWSER_PROFILE_PATH: Path = DATA_PATH / "browser_profile"
    HCAPTCHA_PATH: Path = DATA_PATH / "hcaptcha"
    LOGS_PATH: Path = DATA_PATH / "logs"
    RECORDS_PATH: Path = DATA_PATH / "records"

    cache_dir: Path = HCAPTCHA_PATH / ".cache"
    challenge_dir: Path = HCAPTCHA_PATH / ".challenge"
    captcha_response_dir: Path = HCAPTCHA_PATH / ".captcha"

    @classmethod
    @field_validator(
        "EPIC_GAMES_EMAIL",
        "EPIC_GAMES_PASSWORD",
        "EPIC_GAMES_LOCALE",
        "EPIC_GAMES_COUNTRY",
        mode="before"
    )
    def validate_required_envs(cls, value: Any, info: FieldValidationInfo) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Required environment variable is missing or empty: {info.field_name}")
        return value

config: Config = Config()
