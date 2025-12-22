from hcaptcha_challenger import AgentV
from playwright.async_api import Page, Locator, Response
from gatekeeper.config import config

class CaptchaUtils:
    @staticmethod
    async def wait_for_challenge(page: Page) -> None:
        agent: AgentV = AgentV(page=page, agent_config=config)
        await agent.wait_for_challenge()
