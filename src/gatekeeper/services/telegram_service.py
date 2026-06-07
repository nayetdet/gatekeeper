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

        message = "\n".join(
            line
            for line in [
                "🤖 Gatekeeper — Resumo da Execução",
                "",
                f"📅 Data/Hora: {FileUtils.get_timestamp()}",
                f"📊 Status: {'✅ Sucesso' if success else '❌ Erro'}",
                *(
                    [
                        "",
                        f"🔎 Total: {summary.total}",
                        f"❌ Jogos não resgatados: {summary.failure}",
                        f"✅ Jogos resgatados com sucesso: {summary.success}",
                    ]
                    if not summary.was_skipped
                    else []
                ),
            ]
        )

        logger.info("Sending Telegram notification (message_length={})", len(message))
        try: bot.send_message(chat_id=config.TELEGRAM_BOT_CHAT_ID.get_secret_value(), text=message)
        except Exception:
            logger.exception("Failed to send Telegram notification")
            return

        logger.info("Telegram notification sent successfully")
