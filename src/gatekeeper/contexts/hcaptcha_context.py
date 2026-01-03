from contextlib import suppress, asynccontextmanager
from typing import AsyncIterator
from hcaptcha_challenger import AgentV
from playwright.async_api import Page
from gatekeeper.config import config

class HCaptchaContext:
    @staticmethod
    @asynccontextmanager
    async def get_challenger(page: Page) -> AsyncIterator[AgentV]:
        challenger: AgentV = AgentV(page, agent_config=config)
        try: yield challenger
        finally:
            with suppress(Exception):
                page.remove_listener("response", getattr(challenger, "_task_handler"))
