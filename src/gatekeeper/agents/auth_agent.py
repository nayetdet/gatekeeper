import asyncio
from loguru import logger
from playwright.async_api import Page
from yarl import URL
from gatekeeper.agents.hcaptcha_agent import HCaptchaAgent
from gatekeeper.config import config
from gatekeeper.decorators.retry_decorator import retry
from gatekeeper.events.auth_events import AuthEvents
from gatekeeper.factories.urls.auth_url_factory import AuthUrlFactory
from gatekeeper.factories.urls.store_url_factory import StoreUrlFactory
from gatekeeper.utils.playwright_utils import PlaywrightUtils

class AuthAgent:
    def __init__(self, page: Page) -> None:
        self.__page: Page = page

    @retry(max_attempts=3, wait=5)
    async def login_if_needed(self, hcaptcha_agent: HCaptchaAgent) -> None:
        logger.info("Ensuring authenticated session with Epic Games")
        await self.__handle_redirection()
        if await self.__is_logged_in():
            logger.info("Already logged in, skipping login")
            return

        await self.__handle_login_form(hcaptcha_agent)
        await self.__handle_redirection()

    async def __handle_login_form(self, hcaptcha_agent: HCaptchaAgent) -> None:
        async with AuthEvents(self.__page) as events:
            logger.info("User not authenticated, attempting login")
            await self.__page.goto(str(AuthUrlFactory.build_invalidated_auth_url()), wait_until="domcontentloaded")

            logger.info("Submitting login credentials")
            logger.info("Filling email field")
            await PlaywrightUtils.type(self.__page.locator("#email"), value=config.EPIC_GAMES_EMAIL.get_secret_value())
            await PlaywrightUtils.click(self.__page.locator("#continue"))

            logger.info("Filling password field")
            await PlaywrightUtils.type(self.__page.locator("#password"), value=config.EPIC_GAMES_PASSWORD.get_secret_value())
            await PlaywrightUtils.click(self.__page.locator("#sign-in"))

            logger.info("Waiting for captcha challenge if present")
            await hcaptcha_agent.wait_for_challenge()

            logger.info("Waiting for login success event")
            await asyncio.wait_for(events.login_success.wait(), timeout=60)
            logger.success("Login successful")

    async def __handle_redirection(self) -> None:
        logger.info("Redirecting to auth page")
        await self.__page.goto(str(AuthUrlFactory.build_auth_url()), wait_until="domcontentloaded")

        store_url: URL = StoreUrlFactory.build_store_url()
        logger.info("Redirecting to store: {}", store_url)
        await self.__page.goto(str(store_url), wait_until="domcontentloaded")

    async def __is_logged_in(self) -> bool:
        return await self.__page.locator("//egs-navigation").get_attribute("isloggedin") == "true"
