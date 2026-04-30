from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from gatekeeper.config import config

engine: AsyncEngine = create_async_engine(
    url=f"sqlite+aiosqlite:///{config.DATABASE_PATH.as_posix()}",
    echo=False,
    future=True,
    connect_args={
        "timeout": 30,
        "check_same_thread": False
    }
)

session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False
)
