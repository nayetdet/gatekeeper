import re
import time
from abc import ABC, abstractmethod
from loguru import logger

class BaseJob(ABC):
    @classmethod
    def identifier(cls) -> str:
        name: str = cls.__name__
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    @classmethod
    async def run(cls) -> None:
        job_id: str = cls.identifier()
        logger.info("Starting job: {}", job_id)

        start_time: float = time.perf_counter()
        try:
            await cls()._run()
            elapsed_time: float = time.perf_counter() - start_time
            logger.info("Job finished: {} ({:.2f}s)", job_id, elapsed_time)
        except Exception as e:
            elapsed_time: float = time.perf_counter() - start_time
            logger.exception("Job failed: {} ({:.2f}s)", job_id, elapsed_time)
            raise e

    @abstractmethod
    async def _run(self) -> None:
        raise NotImplementedError
