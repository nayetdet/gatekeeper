import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from gatekeeper.schedulers.claim_scheduler import claim_games

async def main() -> None:
    scheduler: AsyncIOScheduler = AsyncIOScheduler()
    _ = asyncio.create_task(claim_games())

    scheduler.add_job(
        lambda: asyncio.create_task(claim_games()),
        trigger=IntervalTrigger(days=1),
        id="claim_games",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
