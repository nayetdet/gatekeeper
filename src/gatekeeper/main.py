import asyncio
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from gatekeeper.config import config
from gatekeeper.database import engine
from gatekeeper.jobs.claim_job import ClaimJob
from gatekeeper.logger import setup_logger

async def run_once() -> None:
    logger.info("Running app in single-run mode")
    await ClaimJob.run()

async def run_scheduler() -> None:
    logger.info("Running app in scheduler mode (cron='{}')", config.CRONTAB)
    scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=timezone.utc)
    scheduler.add_job(
        ClaimJob.run,
        trigger=CronTrigger.from_crontab(config.CRONTAB),
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

async def main() -> None:
    setup_logger()
    try: await (run_once if not config.CRONTAB else run_scheduler)()
    finally:
        await engine.dispose()
        await logger.complete()

if __name__ == "__main__":
    asyncio.run(main())
