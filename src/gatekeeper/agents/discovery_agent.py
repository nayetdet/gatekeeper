from playwright.async_api import Page, Locator
from yarl import URL
from gatekeeper.decorators.retry_decorator import retry
from gatekeeper.enums.product_path_type import ProductPathType
from gatekeeper.factories.store_url_factory import StoreUrlFactory
from gatekeeper.schemas.product_schema import ProductSchema

class DiscoveryAgent:
    def __init__(self, page: Page) -> None:
        self.__page: Page = page

    async def get_product_url(self, product: ProductSchema) -> URL:
        path_type: ProductPathType = await self.__get_product_path_type(product.slug)
        return StoreUrlFactory.get_store_product_url(product.slug, path_type=path_type)

    @retry(max_attempts=3, wait=5)
    async def __get_product_path_type(self, slug: str) -> ProductPathType:
        for ptype in ProductPathType:
            await self.__page.goto(str(StoreUrlFactory.get_store_product_url(slug, ptype)), wait_until="networkidle")
            error_view: Locator = self.__page.locator("//div[@data-component='ErrorView']")
            error_box: Locator = self.__page.locator("//div[@class='error-box']")
            if await error_view.count() == 0 and await error_box.count() == 0:
                return ptype
        raise LookupError(f"Product not found: {slug}")
