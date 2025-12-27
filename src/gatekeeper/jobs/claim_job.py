from gatekeeper.jobs.base_job import BaseJob
from gatekeeper.services.claim_service import ClaimService

class ClaimJob(BaseJob):
    async def _run(self) -> None:
        await ClaimService.claim_games()
