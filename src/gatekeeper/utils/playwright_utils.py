from playwright.async_api import Locator, expect
from gatekeeper.decorators.retry_decorator import retry

class PlaywrightUtils:
    @staticmethod
    @retry(max_attempts=3, wait=10)
    async def count(element: Locator) -> int:
        return await element.count()

    @staticmethod
    @retry(max_attempts=3, wait=10)
    async def type(locator: Locator, value: str) -> None:
        await expect(locator).to_be_visible()
        await expect(locator).to_be_editable()
        await locator.clear()
        await locator.type(value)

    @staticmethod
    @retry(max_attempts=3, wait=10)
    async def click(locator: Locator) -> None:
        await expect(locator).to_be_visible()
        await expect(locator).to_be_enabled()
        await locator.scroll_into_view_if_needed()
        await locator.click(trial=True)
        await locator.click()
