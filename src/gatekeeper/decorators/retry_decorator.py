from loguru import logger
from tenacity import retry as tenacity_retry, stop_after_attempt, wait_fixed, before_log, before_sleep_log, after_log

def retry(max_attempts: int, wait: int):
    return tenacity_retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_fixed(wait),
        before=before_log(logger, log_level="INFO"), # type: ignore
        before_sleep=before_sleep_log(logger, log_level="WARNING"), # type: ignore
        after=after_log(logger, log_level="INFO"), # type: ignore
        reraise=True
    )
