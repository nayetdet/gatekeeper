from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("offer_id", "namespace"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    offer_id: str = Field(index=True, nullable=False)
    namespace: str = Field(index=True, nullable=False)
    slug: str = Field(nullable=False)
