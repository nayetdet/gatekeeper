import textwrap
from loguru import logger
from telebot import TeleBot
from gatekeeper.config import config
from gatekeeper.schemas.product_claim_summary_schema import ProductClaimSummarySchema
from gatekeeper.utils.file_utils import FileUtils

bot = TeleBot(config.TELEGRAM_BOT_TOKEN.get_secret_value()) if config.TELEGRAM_BOT_ENABLED else None

class TelegramService:
    @staticmethod
    def notify(summary: ProductClaimSummarySchema, success: bool = True) -> None:
        if not config.TELEGRAM_BOT_ENABLED:
            logger.info("Skipping Telegram notification: bot is disabled")
            return

        message: str = textwrap.dedent(
            f"""
            🤖 Gatekeeper — Resumo da Execução

            📅 Data/Hora: {FileUtils.get_timestamp()}
            📊 Status: {"✅ Sucesso" if success else "❌ Erro"}

            {textwrap.dedent(
                f'''
                🔎 Total: {summary.total}
                ❌ Jogos não resgatados: {summary.failure}
                ✅ Jogos resgatados com sucesso: {summary.success}
                '''
            ).strip() if not summary.was_skipped else ""}
            """
        ).strip()

        logger.info("Sending Telegram notification (message_length={})", len(message))
        try: bot.send_message(chat_id=config.TELEGRAM_BOT_CHAT_ID.get_secret_value(), text=message)
        except Exception:
            logger.exception("Failed to send Telegram notification")
            return

        logger.info("Telegram notification sent successfully")
