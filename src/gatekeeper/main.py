import asyncio
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from gatekeeper.schedules.claim_games_task import claim_games_task

async def main() -> None:
    scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        claim_games_task,
        trigger=IntervalTrigger(days=1),
        id=claim_games_task.__name__,
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
    asyncio.run(main())
