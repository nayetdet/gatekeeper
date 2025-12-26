from playwright.async_api import Locator, Page

class PlaywrightUtils:
    @staticmethod
    async def submit_input(page: Page, input_selector: str, button_selector: str, value: str) -> None:
        input_element: Locator = page.locator(input_selector)
        await input_element.clear()
        await input_element.type(value)
        await page.locator(button_selector).click()
