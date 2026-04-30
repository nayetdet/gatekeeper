from loguru import logger
from gatekeeper.config import config
from gatekeeper.utils.file_utils import FileUtils

def setup_logging() -> None:
    logger.add(
        sink=FileUtils.get_file_path(extension="log", base_directory=config.LOGS_PATH),
        enqueue=True,
        backtrace=True,
        diagnose=False
    )
