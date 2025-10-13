import asyncio
from contextlib import suppress
from typing import Dict, Any
from hcaptcha_challenger import AgentV
from playwright.async_api import Page, Locator, Response
from src.rataria_epic_games.config import config

class EpicGamesAgent:
    AUTH_URL: str = "https://www.epicgames.com/account/personal?lang=pt-BR&productName=egs&sessionInvalidated=true"

    def __init__(self, page: Page) -> None:
        self.__page: Page = page
        self.__agent: AgentV = AgentV(page=page, agent_config=config)
        self.__login_success_event: asyncio.Event = asyncio.Event()

    async def claim_game(self, url: str) -> None:
        self.__page.on(event="response", f=self.__on_response)
        await self.__page.goto(url, wait_until="domcontentloaded")
        if await self.__page.locator("//egs-navigation").get_attribute("isloggedin") != "true":
            await self.__login(url)

        purchase_button: Locator = self.__page.locator("[data-testid='purchase-cta-button']")
        if not await purchase_button.get_attribute("disabled"):
            await purchase_button.click()
            await self.__page.frame_locator("//iframe[@class='']").locator("//button[contains(@class, 'payment-btn')]").click()
            await self.__agent.wait_for_challenge()

    async def __login(self, redirect_url: str) -> None:
        await self.__page.goto(self.AUTH_URL, wait_until="domcontentloaded")
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
            await asyncio.wait_for(self.__login_success_event.wait(), timeout=15)
        await self.__page.goto(redirect_url, wait_until="domcontentloaded")

    async def __on_response(self, response: Response) -> None:
        if response.request.method != "POST" or "talon" in response.url:
            return

        with suppress(Exception):
            result: Dict[str, Any] = await response.json()
            if "/id/api/analytics" in response.url and result.get("accountId"):
                self.__login_success_event.set()
