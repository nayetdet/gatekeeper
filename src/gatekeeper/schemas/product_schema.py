from pydantic import BaseModel

class ProductSchema(BaseModel):
    offer_id: str
    namespace: str
    slug: str
