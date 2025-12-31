import asyncio
from loguru import logger
from playwright.async_api import Page
from yarl import URL
from gatekeeper.agents.hcaptcha_agent import HCaptchaAgent
from gatekeeper.config import config
from gatekeeper.decorators.retry_decorator import retry
from gatekeeper.events.auth_events import AuthEvents
from gatekeeper.utils.playwright_utils import PlaywrightUtils

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
    async def login_if_needed(self, hcaptcha_agent: HCaptchaAgent, redirect_url: URL) -> None:
        logger.info("Ensuring authenticated session with Epic Games (redirect_url={})", redirect_url)
        await self.__handle_redirection(redirect_url)
        if await self.__is_logged_in():
            logger.info("Already logged in, skipping login")
            return

        await self.__handle_login_form(hcaptcha_agent)
        await self.__handle_redirection(redirect_url)

    async def __handle_login_form(self, hcaptcha_agent: HCaptchaAgent) -> None:
        async with AuthEvents(self.__page) as events:
            logger.info("User not authenticated, attempting login")
            await self.__page.goto(str(self.get_invalidated_auth_url()), wait_until="domcontentloaded")

            logger.info("Submitting login credentials")
            logger.info("Filling email field")
            await PlaywrightUtils.type(self.__page.locator("#email"), value=config.EPIC_GAMES_EMAIL)
            await PlaywrightUtils.click(self.__page.locator("#continue"))

            logger.info("Filling password field")
            await PlaywrightUtils.type(self.__page.locator("#password"), value=config.EPIC_GAMES_PASSWORD)
            await PlaywrightUtils.click(self.__page.locator("#sign-in"))

            logger.info("Waiting for captcha challenge if present")
            await hcaptcha_agent.wait_for_challenge()

            logger.info("Waiting for login success event")
            await asyncio.wait_for(events.login_success.wait(), timeout=60)
            logger.success("Login successful")

    async def __handle_redirection(self, redirect_url: URL) -> None:
        logger.info("Redirecting to auth page")
        await self.__page.goto(str(self.get_auth_url()), wait_until="domcontentloaded")

        logger.info("Redirecting to target page: {}", redirect_url)
        await self.__page.goto(str(redirect_url), wait_until="domcontentloaded")

    async def __is_logged_in(self) -> bool:
        return await self.__page.locator("//egs-navigation").get_attribute("isloggedin") == "true"
