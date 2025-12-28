import asyncio
from loguru import logger
from playwright.async_api import Page, Locator, expect
from yarl import URL
from gatekeeper.agents.captcha_agent import CaptchaAgent
from gatekeeper.config import config
from gatekeeper.decorators.retry_decorator import retry
from gatekeeper.events.auth_events import AuthEvents

class AuthAgent:
    __BASE_AUTH_URL: URL = URL("https://www.epicgames.com/account/personal")

    def __init__(self, page: Page) -> None:
        self.__page: Page = page

    @classmethod
    def get_auth_url(cls) -> URL:
        lang: str = config.EPIC_GAMES_LOCALE
        return cls.__BASE_AUTH_URL.with_query(
            {
                "lang": lang
            }
        )

    @classmethod
    def get_invalidated_auth_url(cls) -> URL:
        return cls.get_auth_url().update_query(
            {
                "productName": "egs",
                "sessionInvalidated": "true"
            }
        )

    @retry(max_attempts=5, wait=10)
    async def login_if_needed(self, captcha_agent: CaptchaAgent, redirect_url: URL) -> None:
        logger.info("Ensuring authenticated session with Epic Games (redirect_url={})", redirect_url)
        async with AuthEvents(self.__page) as events:
            await self.__handle_redirection(redirect_url)
            if await self.__page.locator("//egs-navigation").get_attribute("isloggedin") == "true":
                logger.info("Already logged in, skipping login flow")
                return

            logger.info("Not authenticated, starting login flow")
            await self.__page.goto(str(self.get_invalidated_auth_url()), wait_until="domcontentloaded")

            logger.info("Submitting login credentials")
            await self.__handle_input_submission(input_selector="#email", button_selector="#continue", value=config.EPIC_GAMES_EMAIL)
            await self.__handle_input_submission(input_selector="#password", button_selector="#sign-in", value=config.EPIC_GAMES_PASSWORD)

            logger.info("Waiting for captcha challenge if present")
            await captcha_agent.wait_for_challenge()

            logger.info("Waiting for login success event")
            await asyncio.wait_for(events.login_success.wait(), timeout=60)
            logger.success("Login successful")

        logger.info("Redirecting back to target page")
        await self.__handle_redirection(redirect_url)

    @retry(max_attempts=3, wait=5)
    async def __handle_input_submission(self, input_selector: str, button_selector: str, value: str) -> None:
        input_element: Locator = self.__page.locator(input_selector)
        await expect(input_element).to_be_visible()
        await expect(input_element).to_be_editable()
        await input_element.clear()
        await input_element.type(value)

        button_element: Locator = self.__page.locator(button_selector)
        await expect(button_element).to_be_visible()
        await expect(button_element).to_be_enabled()
        await button_element.scroll_into_view_if_needed()
        await button_element.click()

    async def __handle_redirection(self, redirect_url: URL) -> None:
        await self.__page.goto(str(self.get_auth_url()), wait_until="domcontentloaded")
        await self.__page.goto(str(redirect_url), wait_until="domcontentloaded")
