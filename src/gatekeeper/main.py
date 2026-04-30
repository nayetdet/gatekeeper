import asyncio
from gatekeeper.logging import setup_logging
from gatekeeper.schemas.product_claim_summary_schema import ProductClaimSummarySchema
from gatekeeper.services.claim_service import ClaimService
from gatekeeper.services.telegram_service import TelegramService

async def main() -> None:
    summary: ProductClaimSummarySchema = ProductClaimSummarySchema()
    try: await ClaimService.claim_products(summary)
    except Exception:
        TelegramService.notify(summary, success=False)
        raise
    else: TelegramService.notify(summary)

if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
