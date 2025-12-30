from typing import Optional
from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True, unique=True, nullable=False)
