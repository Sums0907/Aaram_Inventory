from uuid import UUID
from typing import List
from pydantic import BaseModel

class InventoryConfidenceResponse(BaseModel):
    sku_id: UUID
    confidence_score: int
    positive_signals: List[str]
    negative_signals: List[str]
