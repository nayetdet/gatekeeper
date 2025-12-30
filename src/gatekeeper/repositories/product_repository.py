from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from gatekeeper.database import engine
from gatekeeper.models.product import Product

class ProductRepository:
    @staticmethod
    async def get_by_url(url: str) -> Optional[Product]:
        async with AsyncSession(engine) as session:
            result = await session.exec(select(Product).where(Product.url == url))
            return result.first()

    @staticmethod
    async def create(product: Product) -> Optional[Product]:
        async with AsyncSession(engine) as session:
            try:
                session.add(product)
                await session.commit()
                await session.refresh(product)
                return product
            except IntegrityError:
                await session.rollback()
                return None
