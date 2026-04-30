from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from gatekeeper.database import session_maker
from gatekeeper.models.product import Product

class ProductRepository:
    @staticmethod
    async def get_by_offer_id_and_namespace(offer_id: str, namespace: str) -> Optional[Product]:
        async with session_maker() as session:
            result = await session.execute(select(Product).where((Product.offer_id == offer_id) & (Product.namespace == namespace)))
            return result.first()

    @staticmethod
    async def create(product: Product) -> Optional[Product]:
        async with session_maker() as session:
            try:
                session.add(product)
                await session.commit()
                await session.refresh(product)
                return product
            except IntegrityError:
                await session.rollback()
                return None
