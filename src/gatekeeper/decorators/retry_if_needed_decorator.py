from typing import Callable, Optional, overload
from loguru import logger
from tenacity import WrappedFn, after_log, before_log, stop_after_attempt, wait_fixed, retry as tenacity_retry

DEFAULT_MAX_ATTEMPTS: int = 3
DEFAULT_WAIT: int = 5

@overload
def retry_if_needed(
    fn: WrappedFn,
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    wait: int = DEFAULT_WAIT
) -> WrappedFn: ...

@overload
def retry_if_needed(
    fn: None = None,
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    wait: int = DEFAULT_WAIT
) -> Callable[[WrappedFn], WrappedFn]: ...

def retry_if_needed(
    fn: Optional[WrappedFn] = None,
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    wait: int = DEFAULT_WAIT
) -> WrappedFn | Callable[[WrappedFn], WrappedFn]:
    wrapper: WrappedFn = tenacity_retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_fixed(wait),
        before=before_log(logger, log_level="DEBUG"), # type: ignore[arg-type]
        before_sleep=lambda retry_state: logger.opt(exception=retry_state.outcome.exception() if retry_state.outcome.failed else None).log(
            "WARNING",
            "Retrying fn={fn} sleep={sleep:.3g}s attempt={attempt} status={status} value={value}",
            fn=retry_state.fn.__name__ if retry_state.fn else "<unknown>",
            sleep=retry_state.next_action.sleep if retry_state.next_action else retry_state.upcoming_sleep,
            attempt=retry_state.attempt_number,
            status="raised" if retry_state.outcome.failed else "returned",
            value=f"{type(retry_state.outcome.exception()).__name__}: {retry_state.outcome.exception()}" if retry_state.outcome.failed else retry_state.outcome.result()
        ),
        after=after_log(logger, log_level="DEBUG"), # type: ignore[arg-type]
        reraise=True
    )

    return wrapper(fn) if fn is not None else wrapper
