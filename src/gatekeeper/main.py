import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from gatekeeper.schedulers.claim_scheduler import claim_games

async def main() -> None:
    await claim_games()
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        claim_games,
        trigger=IntervalTrigger(days=1),
        id="claim_games",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()
    try: await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)

if __name__ == "__main__":
    asyncio.run(main())
