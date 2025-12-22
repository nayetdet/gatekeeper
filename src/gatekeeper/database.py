from sqlalchemy.ext.asyncio import create_async_engine
from gatekeeper.config import Config

engine = create_async_engine(
    url=f"sqlite+aiosqlite:///{Config.Paths.DATA / "database.sqlite"}",
    echo=False,
    connect_args={
        "timeout": 30
    }
)
