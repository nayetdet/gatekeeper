from gatekeeper.models import Product
from gatekeeper.schemas.product_schema import ProductSchema

class ProductMapper:
    @staticmethod
    def to_model(product: ProductSchema) -> Product:
        return Product(
            offer_id=product.offer_id,
            namespace=product.namespace,
            slug=product.slug
        )

    @staticmethod
    def to_schema(offer_id: str, namespace: str, slug: str) -> ProductSchema:
        return ProductSchema(offer_id=offer_id, namespace=namespace, slug=slug)
