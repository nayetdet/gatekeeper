import asyncio
from asyncio import Event
from contextlib import suppress
from typing import Dict, Any
from playwright.async_api import Page, Locator, Response
from yarl import URL
from gatekeeper.config import config
from gatekeeper.models.game import Game
from gatekeeper.repositories.game_repository import GameRepository
from gatekeeper.utils.captcha_utils import CaptchaUtils

class SessionService:
    BASE_AUTH_URL: URL = URL("https://www.epicgames.com/account/personal")

    def __init__(self, page: Page, locale: str) -> None:
        self.__page: Page = page
        self.__locale: str = locale
        self.__login_success_event: Event = Event()

    def get_auth_url(self) -> URL:
        return self.BASE_AUTH_URL.with_query(
            {
                "lang": self.__locale,
                "productName": "egs",
                "sessionInvalidated": "true"
            }
        )

    async def claim_game(self, url: URL) -> None:
        await self.login_if_needed(url)
        purchase_button: Locator = self.__page.locator("[data-testid='purchase-cta-button']")
        if not await purchase_button.get_attribute("disabled"):
            await purchase_button.click()
            await self.__page.frame_locator("//iframe[@class='']").locator("//button[contains(@class, 'payment-btn')]").click()
            await CaptchaUtils.wait_for_challenge(self.__page)
        await GameRepository.create(Game(url=str(url)))

    async def login_if_needed(self, redirect_url: URL) -> None:
        self.__login_success_event.clear()
        self.__page.on(event="response", f=self.__on_response)

        try:
            await self.__page.goto(str(redirect_url), wait_until="domcontentloaded")
            if await self.__page.locator("//egs-navigation").get_attribute("isloggedin") == "true":
                return

            await self.__page.goto(str(self.get_auth_url()), wait_until="domcontentloaded")
            email_input: Locator = self.__page.locator("#email")
            await email_input.clear()
            await email_input.type(config.EpicGames.EMAIL)
            await self.__page.click("#continue")

            password_input: Locator = self.__page.locator("#password")
            await password_input.clear()
            await password_input.type(config.EpicGames.PASSWORD)
            await self.__page.click("#sign-in")

            await CaptchaUtils.wait_for_challenge(self.__page)
            with suppress(asyncio.TimeoutError):
                await asyncio.wait_for(self.__login_success_event.wait(), timeout=15)
            await self.__page.goto(str(redirect_url), wait_until="domcontentloaded")
        finally: self.__page.remove_listener("response", self.__on_response)

    async def __on_response(self, response: Response) -> None:
        if response.request.method != "POST" or "talon" in response.url:
            return

        with suppress(Exception):
            result: Dict[str, Any] = await response.json()
            if "/id/api/analytics" in response.url and result.get("accountId"):
                self.__login_success_event.set()
