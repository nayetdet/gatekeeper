from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from gatekeeper.database import engine
from gatekeeper.models.product import Product

class ProductRepository:
    @staticmethod
    async def get_by_offer_id_and_namespace(offer_id: str, namespace: str) -> Optional[Product]:
        async with AsyncSession(engine) as session:
            result = await session.exec(select(Product).where((Product.offer_id == offer_id) & (Product.namespace == namespace)))
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
