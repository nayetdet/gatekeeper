from playwright.async_api import Locator, ViewportSize
from gatekeeper.decorators.retry_decorator import retry

class PlaywrightUtils:
    @staticmethod
    async def init_cursor(locator: Locator) -> None:
        viewport: ViewportSize = locator.page.viewport_size
        x: float = viewport["width"] // 2
        y: float = viewport["height"] // 2
        await locator.page.mouse.move(x - 50, y - 50)
        await locator.page.mouse.move(x, y)

    @staticmethod
    @retry(max_attempts=3, wait=5)
    async def count(element: Locator) -> int:
        return await element.count()

    @staticmethod
    @retry(max_attempts=3, wait=5)
    async def type(locator: Locator, value: str) -> None:
        await locator.wait_for(state="visible")
        await locator.scroll_into_view_if_needed()
        await locator.clear()
        await locator.type(value)

    @classmethod
    @retry(max_attempts=3, wait=5)
    async def click(cls, locator: Locator, trial: bool = False) -> None:
        await cls.init_cursor(locator)
        await locator.wait_for(state="visible")
        await locator.scroll_into_view_if_needed()
        await locator.click(timeout=2500)
