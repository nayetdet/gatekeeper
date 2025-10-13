from os import getenv
from pathlib import Path
from hcaptcha_challenger import AgentConfig

class Config(AgentConfig):
    class EpicGames:
        EMAIL: str = getenv("EPIC_GAMES_EMAIL")
        PASSWORD: str = getenv("EPIC_GAMES_PASSWORD")

    class Paths:
        CONFIG_PATH: Path = Path("config")

config: Config = Config()
