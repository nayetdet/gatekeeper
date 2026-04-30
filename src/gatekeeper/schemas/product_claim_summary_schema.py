from pydantic import BaseModel

class ProductClaimSummarySchema(BaseModel):
    was_skipped: bool = False
    total: int = 0
    success: int = 0
    failure: int = 0
