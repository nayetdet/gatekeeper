from playwright.async_api import Locator
from gatekeeper.decorators.retry_decorator import retry

class PlaywrightUtils:
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

    @staticmethod
    @retry(max_attempts=3, wait=5)
    async def click(locator: Locator) -> None:
        await locator.wait_for(state="visible")
        await locator.scroll_into_view_if_needed()
        await locator.click(timeout=5000)
