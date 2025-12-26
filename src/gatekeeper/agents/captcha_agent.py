from contextlib import suppress
from typing import Optional
from hcaptcha_challenger import AgentV
from playwright.async_api import Page
from gatekeeper.config import config

class CaptchaAgent:
    def __init__(self, page: Page) -> None:
        self.__agent: Optional[AgentV] = AgentV(page=page, agent_config=config)

    async def wait_for_challenge(self) -> None:
        if self.__agent:
            await self.__agent.wait_for_challenge()

    def close(self) -> None:
        if not self.__agent:
            return

        with suppress(Exception):
            self.__agent.page.remove_listener(event="response", f=getattr(self.__agent, "_task_handler"))
            self.__agent = None
