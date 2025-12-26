import asyncio
from contextlib import suppress
from typing import List
from hcaptcha_challenger import AgentV
from playwright.async_api import Page, Locator, expect
from yarl import URL
from gatekeeper.config import config
from gatekeeper.events.session_events import SessionEvents
from gatekeeper.models.game import Game
from gatekeeper.repositories.game_repository import GameRepository

class SessionService:
    BASE_AUTH_URL: URL = URL("https://www.epicgames.com/account/personal")

    def __init__(self, page: Page, locale: str) -> None:
        self.__page: Page = page
        self.__locale: str = locale
        self.__agent: AgentV = AgentV(page=self.__page, agent_config=config)
        self.__events: SessionEvents = SessionEvents()

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
            await self.__agent.wait_for_challenge()
        await GameRepository.create(Game(url=str(url)))

    async def login_if_needed(self, redirect_url: URL) -> None:
        async with self.__events.listen(self.__page):
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

            await self.__agent.wait_for_challenge()
            with suppress(asyncio.TimeoutError):
                await asyncio.wait_for(self.__events.login_success.wait(), timeout=60)

            await asyncio.wait_for(self.__handle_post_login(), timeout=60)
            await self.__page.goto(str(redirect_url), wait_until="domcontentloaded")

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
