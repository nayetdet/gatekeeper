from loguru import logger
from playwright.async_api import Page, Locator, FrameLocator
from yarl import URL
from gatekeeper.agents.captcha_agent import CaptchaAgent
from gatekeeper.decorators.retry_decorator import retry
from gatekeeper.models.game import Game
from gatekeeper.repositories.game_repository import GameRepository
from gatekeeper.utils.playwright_utils import PlaywrightUtils

class ClaimAgent:
    def __init__(self, page: Page) -> None:
        self.__page: Page = page

    @retry(max_attempts=5, wait=10)
    async def claim_game(self, captcha_agent: CaptchaAgent, url: URL) -> None:
        logger.info("Starting game claim: {}", url)
        await self.__page.goto(str(url), wait_until="domcontentloaded")
        if not await self.__is_already_claimed():
            await self.__handle_purchase(captcha_agent)
        else: logger.warning("Game already owned or unavailable, purchase skipped")
        logger.success("Game claim completed, saving to database (url={})", url)
        await GameRepository.create(Game(url=str(url)))

    async def __handle_purchase(self, captcha_agent: CaptchaAgent) -> None:
        logger.info("Attempting purchase")
        logger.info("Clicking purchase button")
        purchase_button: Locator = self.__page.locator("//aside//button[@data-testid='purchase-cta-button']")
        await PlaywrightUtils.click(purchase_button)

        logger.info("Clicking payment confirmation button")
        iframe: FrameLocator = self.__page.frame_locator("//iframe[@class='']")
        payment_button: Locator = iframe.locator("//button[contains(@class, 'payment-btn')]")
        await PlaywrightUtils.click(payment_button)

        logger.info("Waiting for captcha challenge if present")
        await captcha_agent.wait_for_challenge()
        logger.success("Purchase completed")

    async def __is_already_claimed(self) -> bool:
        cart_button: Locator = self.__page.locator("//aside//button[@data-testid='add-to-cart-cta-button-pdp-sidebar']")
        return await cart_button.count() == 0
