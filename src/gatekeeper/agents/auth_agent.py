import asyncio
import logging
from contextlib import suppress
from loguru import logger
from typing import List
from playwright.async_api import Page, Locator, expect
from tenacity import retry, stop_after_attempt, wait_fixed, before_log, before_sleep_log
from yarl import URL
from gatekeeper.agents.captcha_agent import CaptchaAgent
from gatekeeper.config import config
from gatekeeper.events.auth_events import SessionEvents
from gatekeeper.utils.playwright_utils import PlaywrightUtils

class AuthAgent:
    BASE_AUTH_URL: URL = URL("https://www.epicgames.com/account/personal")

    def __init__(self, page: Page) -> None:
        self.__page: Page = page

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(5),
        before=before_log(logger, logging.INFO),
        before_sleep=before_sleep_log(logger, log_level=logging.WARNING),
        reraise=True
    )
    async def login_if_needed(self, captcha_agent: CaptchaAgent, redirect_url: URL) -> None:
        logger.info("Ensuring authenticated session (redirect={})", redirect_url)
        async with SessionEvents(self.__page) as events:
            await self.__page.goto(str(redirect_url), wait_until="domcontentloaded")
            if await self.__page.locator("//egs-navigation").get_attribute("isloggedin") == "true":
                logger.info("Already logged in, skipping login flow")
                return

            logger.info("Not authenticated, starting login flow")
            await self.__page.goto(str(self.get_auth_url()), wait_until="domcontentloaded")
            await PlaywrightUtils.submit_input(page=self.__page, input_selector="#email", button_selector="#continue", value=config.EPIC_GAMES_EMAIL)
            await PlaywrightUtils.submit_input(page=self.__page, input_selector="#password", button_selector="#sign-in", value=config.EPIC_GAMES_PASSWORD)
            await captcha_agent.wait_for_challenge()

            with suppress(asyncio.TimeoutError):
                await asyncio.wait_for(events.login_success.wait(), timeout=60)
                logger.info("Login successful")

            with suppress(asyncio.TimeoutError):
                await asyncio.wait_for(self.__handle_post_login(events), timeout=60)
                logger.info("Post login successful")

            logger.info("Login flow finished: redirecting back to target page")
            await self.__page.goto(str(redirect_url), wait_until="domcontentloaded")

    async def __handle_post_login(self, events: SessionEvents) -> None:
        button_ids: List[str] = [
            "#link-success",
            "#login-reminder-prompt-setup-tfa-skip",
            "#yes"
        ]

        await self.__page.goto(str(self.BASE_AUTH_URL), wait_until="networkidle")
        while not events.csrf_refresh.is_set() and button_ids:
            await self.__page.wait_for_timeout(500)
            for button_id in button_ids.copy():
                with suppress(Exception):
                    reminder_button: Locator = self.__page.locator(button_id)
                    await expect(reminder_button).to_be_visible()
                    await reminder_button.click()
                    button_ids.remove(button_id)
