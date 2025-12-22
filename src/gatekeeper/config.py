from os import getenv
from pathlib import Path
from hcaptcha_challenger import AgentConfig

class Config(AgentConfig):
    class EpicGames:
        EMAIL: str = getenv("EPIC_GAMES_EMAIL")
        PASSWORD: str = getenv("EPIC_GAMES_PASSWORD")
        LOCALE: str = getenv("EPIC_GAMES_LOCALE")
        COUNTRY: str = getenv("EPIC_GAMES_COUNTRY")

    class Paths:
        ROOT: Path = Path(__file__).resolve().parents[2]
        CONFIG: Path = ROOT / "config"
        DATA: Path = ROOT / "data"

config: Config = Config()
