import asyncio
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from gatekeeper.config import config
from gatekeeper.database import engine
from gatekeeper.jobs.claim_job import ClaimJob
from gatekeeper.logger import setup_logger

async def main() -> None:
    setup_logger()
    if not config.EPIC_GAMES_CRONTAB:
        await ClaimJob.run()
        return

    scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=timezone.utc)
    scheduler.add_job(
        ClaimJob.run,
        trigger=CronTrigger.from_crontab(config.EPIC_GAMES_CRONTAB),
        id=ClaimJob.identifier(),
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now(timezone.utc)
    )

    scheduler.start()
    try: await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)

if __name__ == "__main__":
    try: asyncio.run(main())
    finally:
        logger.complete()
        asyncio.run(engine.dispose())
