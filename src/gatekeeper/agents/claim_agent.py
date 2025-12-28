from loguru import logger
from playwright.async_api import Page, Locator, expect, FrameLocator
from yarl import URL
from gatekeeper.agents.captcha_agent import CaptchaAgent
from gatekeeper.decorators.retry_decorator import retry
from gatekeeper.models.game import Game
from gatekeeper.repositories.game_repository import GameRepository

class ClaimAgent:
    def __init__(self, page: Page) -> None:
        self.__page: Page = page

    @retry(max_attempts=5, wait=10)
    async def claim_game(self, captcha_agent: CaptchaAgent, url: URL) -> None:
        logger.info("Starting claim flow for game: {}", url)
        if url != URL(self.__page.url):
            logger.info("Navigating to game page (from={}, to={})", self.__page.url, url)
            await self.__page.goto(str(url), wait_until="domcontentloaded")
        else: logger.info("Already on game page, navigation skipped")

        await self.__handle_purchase(captcha_agent)
        logger.success("Claim flow completed, persisting game to database (url={})", url)
        await GameRepository.create(Game(url=str(url)))

    async def __handle_purchase(self, captcha_agent: CaptchaAgent) -> None:
        purchase_button: Locator = self.__page.locator("//aside//button[@data-testid='purchase-cta-button']")
        await expect(purchase_button).to_be_visible()
        if await purchase_button.is_disabled():
            logger.warning("Purchase button disabled, game already owned or unavailable")
            return

        logger.info("Purchase button enabled, attempting checkout")
        await purchase_button.scroll_into_view_if_needed()
        await purchase_button.click()
        await self.__handle_purchase_confirmation()

        logger.info("Waiting for captcha challenge if present")
        await captcha_agent.wait_for_challenge()

    async def __handle_purchase_confirmation(self) -> None:
        iframe: FrameLocator = self.__page.frame_locator("//iframe[@class='']")
        payment_button: Locator = iframe.locator("//button[contains(@class, 'payment-btn')]")
        await expect(payment_button).to_be_enabled()
        await payment_button.scroll_into_view_if_needed()
        await payment_button.click()
