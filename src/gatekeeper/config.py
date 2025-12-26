from os import getenv
from pathlib import Path
from hcaptcha_challenger import AgentConfig, FastShotModelType, SCoTModelType
from pydantic import Field

class Config(AgentConfig):
    # Epic Games
    EPIC_GAMES_EMAIL: str = Field(default_factory=lambda: getenv("EPIC_GAMES_EMAIL"))
    EPIC_GAMES_PASSWORD: str = Field(default_factory=lambda: getenv("EPIC_GAMES_PASSWORD"))
    EPIC_GAMES_LOCALE: str = Field(default_factory=lambda: getenv("EPIC_GAMES_LOCALE"))
    EPIC_GAMES_COUNTRY: str = Field(default_factory=lambda: getenv("EPIC_GAMES_COUNTRY"))

    # Agent Config
    MODEL: str = "gemini-2.5-flash"
    CHALLENGE_CLASSIFIER_MODEL: FastShotModelType = MODEL
    IMAGE_CLASSIFIER_MODEL: SCoTModelType = MODEL
    SPATIAL_POINT_REASONER_MODEL: SCoTModelType = MODEL
    SPATIAL_PATH_REASONER_MODEL: SCoTModelType = MODEL

    # Paths
    ROOT_PATH: Path = Path(__file__).resolve().parents[2]
    DATA_PATH: Path = ROOT_PATH / "data"
    BROWSER_PROFILE_PATH: Path = DATA_PATH / "browser_profile"

config: Config = Config()
