import asyncio
from camoufox import AsyncCamoufox
from playwright.async_api import Page
from src.rataria_epic_games.agents.epic_games_agent import EpicGamesAgent
from src.rataria_epic_games.config import Config

async def main() -> None:
    async with AsyncCamoufox(
        persistent_context=True,
        user_data_dir=Config.Paths.CONFIG_PATH,
        humanize=1,
        headless=False
    ) as browser:
        page: Page = browser.pages[0] if browser.pages else await browser.new_page()
        agent: EpicGamesAgent = EpicGamesAgent(page=page)
        await agent.claim_game("https://store.epicgames.com/pt-BR/p/gravity-circuit-489baa")
        input()

if __name__ == "__main__":
    asyncio.run(main())
