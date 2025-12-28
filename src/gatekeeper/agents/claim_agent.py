import logging
from contextlib import suppress
from loguru import logger
from playwright.async_api import Page, Locator, expect, FrameLocator
from tenacity import retry, stop_after_attempt, wait_fixed, before_log, before_sleep_log
from yarl import URL
from gatekeeper.agents.captcha_agent import CaptchaAgent
from gatekeeper.models.game import Game
from gatekeeper.repositories.game_repository import GameRepository

class ClaimAgent:
    def __init__(self, page: Page) -> None:
        self.__page: Page = page

    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(5),
        before=before_log(logger, logging.INFO),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def claim_game(self, captcha_agent: CaptchaAgent, url: URL) -> None:
        logger.info("Starting claim flow for game: {}", url)
        await self.__page.goto(str(url), wait_until="domcontentloaded")

        purchase_button: Locator = self.__page.locator("[data-testid='purchase-cta-button']")
        if await purchase_button.is_enabled():
            logger.info("Purchase button enabled, attempting checkout")
            await purchase_button.click()
            await self.__handle_order_confirmation()

            logger.info("Order confirmation completed, awaiting captcha if present")
            await captcha_agent.wait_for_challenge()
        else: logger.warning("Game already owned or unavailable: {}", url)
        logger.success("Persisting claimed game to database: {}", url)
        await GameRepository.create(Game(url=str(url)))

    async def __handle_order_confirmation(self) -> None:
        iframe: FrameLocator = self.__page.frame_locator("//iframe[@class='']")
        payment_container: Locator = iframe.locator("//div[@class='payment-order-confirm']")
        with suppress(Exception):
            await expect(payment_container).to_be_attached()
            await payment_container.focus()

        payment_button: Locator = iframe.locator("//button[contains(@class, 'payment-btn')]")
        await expect(payment_button).to_be_enabled()
        await payment_button.click()
