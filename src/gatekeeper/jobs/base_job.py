import re
from abc import ABC, abstractmethod

class BaseJob(ABC):
    @classmethod
    def identifier(cls) -> str:
        name: str = cls.__name__
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    @classmethod
    async def run(cls) -> None:
        await cls()._run()

    @abstractmethod
    async def _run(self) -> None:
        raise NotImplementedError
