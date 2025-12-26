from sqlalchemy.ext.asyncio import create_async_engine
from gatekeeper.config import config

engine = create_async_engine(
    url=f"sqlite+aiosqlite:///{config.DATA_PATH / "database.sqlite"}",
    echo=False,
    connect_args={
        "timeout": 30
    }
)
