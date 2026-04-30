from datetime import datetime
from pathlib import Path
from loguru import logger
from playwright.async_api import Page
from gatekeeper.config import config
from gatekeeper.utils.file_utils import FileUtils

class PlaywrightSnapshotUtils:
    @classmethod
    async def save_snapshot(cls, page: Page) -> None:
        await cls.save_html(page)
        await cls.save_screenshot(page)

    @staticmethod
    async def save_html(page: Page) -> None:
        url: str = page.url or "about:blank"
        logger.info("Saving HTML snapshot for url={}", url)
        try:
            html: str = await page.evaluate("() => document.documentElement.outerHTML")
            html_path: Path = FileUtils.get_file_path(extension="html", base_directory=FileUtils.get_directory_path(base_directory=config.HTML_PATH), dt=datetime.now())
            html_path.write_text(html, encoding="utf-8")
            logger.info("Saved HTML snapshot for browser; url={}; html_path={}", url, html_path)
        except Exception:
            logger.exception("Failed to save HTML snapshot for browser; url={} html_dir={}", url, config.HTML_PATH)

    @staticmethod
    async def save_screenshot(page: Page) -> None:
        url: str = page.url or "about:blank"
        logger.info("Saving screenshot for url={}", url)
        try:
            screenshot_path: Path = FileUtils.get_file_path(extension="png", base_directory=FileUtils.get_directory_path(base_directory=config.SCREENSHOTS_PATH), dt=datetime.now())
            await page.screenshot(path=screenshot_path)
            logger.info("Saved screenshot for browser; url={}; screenshot_path={}", url, screenshot_path)
        except Exception:
            logger.exception("Failed to save screenshot for browser; url={} screenshots_dir={}", url, config.SCREENSHOTS_PATH)
