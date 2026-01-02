from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from gatekeeper.config import config

engine: AsyncEngine = create_async_engine(
    url=f"sqlite+aiosqlite:///{config.DATABASE_PATH.as_posix()}",
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "timeout": 30,
        "check_same_thread": False
    }
)
