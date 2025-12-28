from contextlib import suppress
from loguru import logger
from playwright.async_api import Page, Locator, expect, FrameLocator
from yarl import URL
from gatekeeper.agents.captcha_agent import CaptchaAgent
from gatekeeper.models.game import Game
from gatekeeper.repositories.game_repository import GameRepository

class ClaimAgent:
    def __init__(self, page: Page) -> None:
        self.__page: Page = page

    async def claim_game(self, captcha_agent: CaptchaAgent, url: URL) -> None:
        logger.info("Starting claim flow for game: {}", url)
        purchase_button: Locator = self.__page.locator("[data-testid='purchase-cta-button']")
        if not await purchase_button.is_disabled():
            logger.info("Purchase button enabled, attempting checkout")
            await purchase_button.click()
            await self.__handle_order_confirmation()

            logger.info("Order confirmation completed, awaiting captcha if present")
            await captcha_agent.wait_for_challenge()
        else: logger.info("Game already owned or unavailable: {}", url)
        logger.success("Persisting claimed game to database: {}", url)
        await GameRepository.create(Game(url=str(url)))

    async def __handle_order_confirmation(self) -> None:
        iframe: FrameLocator = self.__page.frame_locator("//iframe[@class='']")
        payment_container: Locator = iframe.locator("//div[@class='payment-order-confirm']")
        with suppress(Exception):
            await expect(payment_container).to_be_visible()
            await payment_container.focus()

        payment_button: Locator = iframe.locator("//button[contains(@class, 'payment-btn')]")
        await expect(payment_button).to_be_enabled()
        await payment_button.click()
