from playwright.async_api import Locator, TimeoutError
from gatekeeper.decorators.retry_if_needed_decorator import retry_if_needed

class PlaywrightUtils:
    @staticmethod
    @retry_if_needed
    async def click(locator: Locator, force: bool = False) -> None:
        await locator.wait_for(state="visible")
        try: await locator.scroll_into_view_if_needed()
        except TimeoutError:
            pass
        await locator.click(force=force)

    @staticmethod
    @retry_if_needed
    async def type(locator: Locator, value: str) -> None:
        await locator.wait_for(state="visible")
        await locator.scroll_into_view_if_needed()
        await locator.click()
        await locator.fill("")
        await locator.type(value, delay=50, timeout=max(30000, len(value) * 100))

    @staticmethod
    @retry_if_needed
    async def count(element: Locator) -> int:
        return await element.count()
