from datetime import datetime
from loguru import logger
from gatekeeper.config import config

def setup_logger() -> None:
    config.LOGS_PATH.mkdir(parents=True, exist_ok=True)
    logger.add(
        sink=config.LOGS_PATH / f"{datetime.now():%Y%m%dT%H%M%S}.log",
        enqueue=True,
        backtrace=True,
        diagnose=False
    )
