from loguru import logger
from playwright.async_api import Page, Locator, FrameLocator, expect
from yarl import URL
from gatekeeper.agents.hcaptcha_agent import HCaptchaAgent
from gatekeeper.decorators.retry_decorator import retry
from gatekeeper.utils.playwright_utils import PlaywrightUtils

class ClaimAgent:
    def __init__(self, page: Page) -> None:
        self.__page: Page = page

    @retry(max_attempts=3, wait=5)
    async def claim_product(self, hcaptcha_agent: HCaptchaAgent, url: URL) -> None:
        logger.info("Starting product claim: {}", url)
        await self.__page.goto(str(url), wait_until="domcontentloaded")
        await self.__handle_purchase(hcaptcha_agent)

    async def __handle_purchase(self, hcaptcha_agent: HCaptchaAgent) -> None:
        logger.info("Attempting purchase")
        purchase_button: Locator = self.__page.locator("//button[@data-testid='purchase-cta-button']").first
        if await self.__is_already_claimed(purchase_button):
            logger.warning("Product already owned or unavailable, purchase skipped")
            return

        logger.info("Purchase available, clicking purchase button")
        await PlaywrightUtils.click(purchase_button)

        logger.info("Clicking payment confirmation button")
        payment_iframe: FrameLocator = self.__page.frame_locator("//iframe[@class='']")
        payment_button: Locator = payment_iframe.locator("//button[contains(@class, 'payment-btn')]")
        await PlaywrightUtils.click(payment_button)

        logger.info("Waiting for captcha challenge if present")
        await hcaptcha_agent.wait_for_challenge()

        success_container: Locator = self.__page.locator("//div[@data-testid='checkout-success-title']")
        await expect(success_container).to_be_visible()
        logger.success("Purchase successfully completed")

    @staticmethod
    async def __is_already_claimed(purchase_button: Locator) -> bool:
        action_container: Locator = purchase_button.locator("../../div//button")
        action_container_button_count: int = await PlaywrightUtils.count(action_container)
        logger.info("Action buttons detected: {}", action_container_button_count)
        if not action_container_button_count:
            raise RuntimeError("No action buttons found, page layout may have changed or page not fully loaded")
        return action_container_button_count == 1
