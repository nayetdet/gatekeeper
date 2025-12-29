from playwright.async_api import Locator, expect
from gatekeeper.decorators.retry_decorator import retry

class PlaywrightUtils:
    @staticmethod
    @retry(max_attempts=3, wait=5)
    async def type(input_element: Locator, value: str) -> None:
        await expect(input_element).to_be_visible()
        await expect(input_element).to_be_editable()
        await input_element.clear()
        await input_element.type(value)

    @staticmethod
    @retry(max_attempts=3, wait=5)
    async def click(button_element: Locator) -> None:
        await expect(button_element).to_be_visible()
        await expect(button_element).to_be_enabled()
        await button_element.scroll_into_view_if_needed()
        await button_element.click()
