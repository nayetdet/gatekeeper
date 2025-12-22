from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from gatekeeper.database import engine
from gatekeeper.models.game import Game

class GameRepository:
    @classmethod
    async def get_by_url(cls, url: str) -> Optional[Game]:
        async with AsyncSession(engine) as session:
            result = await session.exec(select(Game).where(Game.url == url))
            return result.first()

    @classmethod
    async def create(cls, game: Game) -> Optional[Game]:
        async with AsyncSession(engine) as session:
            try:
                session.add(game)
                await session.commit()
                await session.refresh(game)
                return game
            except IntegrityError:
                await session.rollback()
                return None
