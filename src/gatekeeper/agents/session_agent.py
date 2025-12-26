import asyncio
from contextlib import suppress
from loguru import logger
from typing import List, Self
from playwright.async_api import Page, Locator, expect
from yarl import URL
from gatekeeper.agents.captcha_agent import CaptchaAgent
from gatekeeper.config import config
from gatekeeper.events.session_events import SessionEvents
from gatekeeper.models.game import Game
from gatekeeper.repositories.game_repository import GameRepository
from gatekeeper.utils.playwright_utils import PlaywrightUtils

class SessionAgent:
    BASE_AUTH_URL: URL = URL("https://www.epicgames.com/account/personal")

    def __init__(self, page: Page) -> None:
        self.__page: Page = page
        self.__captcha_agent: CaptchaAgent = CaptchaAgent(page)
        self.__events: SessionEvents = SessionEvents()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:
        self.close()

    @classmethod
    def get_auth_url(cls) -> URL:
        lang: str = config.EPIC_GAMES_LOCALE
        return cls.BASE_AUTH_URL.with_query(
            {
                "lang": lang,
                "productName": "egs",
                "sessionInvalidated": "true"
            }
        )

    async def claim_game(self, url: URL) -> None:
        logger.info("Starting claim flow for game: {}", url)
        await self.login_if_needed(url, max_retries=3)
        purchase_button: Locator = self.__page.locator("[data-testid='purchase-cta-button']")
        if not await purchase_button.is_disabled():
            await purchase_button.click()
            await self.__page.frame_locator("//iframe[@class='']").locator("//button[contains(@class, 'payment-btn')]").click()
            await self.__captcha_agent.wait_for_challenge()
        else: logger.info("Game already owned or unavailable: {}", url)
        logger.info("Persisting claimed game to database: {}", url)
        await GameRepository.create(Game(url=str(url)))

    async def login_if_needed(self, redirect_url: URL, max_retries: int) -> None:
        logger.info("Ensuring authenticated session (redirect={})", redirect_url)
        async with self.__events.listen(self.__page):
            for attempt in range(1, max_retries + 1):
                logger.info("Login attempt {}/{} started", attempt, max_retries)
                await self.__page.goto(str(redirect_url), wait_until="domcontentloaded")
                if await self.__page.locator("//egs-navigation").get_attribute("isloggedin") == "true":
                    logger.info("Already logged in, skipping login flow")
                    return

                try:
                    logger.info("Not authenticated, starting login flow")
                    await self.__page.goto(str(self.get_auth_url()), wait_until="domcontentloaded")
                    await PlaywrightUtils.submit_input(page=self.__page, input_selector="#email", button_selector="#continue", value=config.EPIC_GAMES_EMAIL)
                    await PlaywrightUtils.submit_input(page=self.__page, input_selector="#password", button_selector="#sign-in", value=config.EPIC_GAMES_PASSWORD)
                    await self.__captcha_agent.wait_for_challenge()

                    with suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(self.__events.login_success.wait(), timeout=60)
                        logger.info("Login successful")

                    with suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(self.__handle_post_login(), timeout=60)
                        logger.info("Post login successful")

                    logger.info("Redirecting back to target page")
                    await self.__page.goto(str(redirect_url), wait_until="domcontentloaded")
                    break
                except Exception as e:
                    logger.error("Login attempt {}/{} failed: {}", attempt, max_retries, e)
                    await asyncio.sleep(5)
                    continue
            else: logger.error("Authentication failed after {} attempts", max_retries)

    async def __handle_post_login(self) -> None:
        button_ids: List[str] = [
            "#link-success",
            "#login-reminder-prompt-setup-tfa-skip",
            "#yes"
        ]

        await self.__page.goto(str(self.BASE_AUTH_URL), wait_until="networkidle")
        while not self.__events.csrf_refresh.is_set() and button_ids:
            await self.__page.wait_for_timeout(500)
            for button_id in button_ids.copy():
                with suppress(Exception):
                    reminder_button: Locator = self.__page.locator(button_id)
                    await expect(reminder_button).to_be_visible(timeout=1000)
                    await reminder_button.click(timeout=1000)
                    button_ids.remove(button_id)

    def close(self) -> None:
        self.__captcha_agent.close()
