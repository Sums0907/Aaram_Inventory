from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import Field
from src.foundation.validation.base import BaseSchema

class InventoryBalanceBase(BaseSchema):
    warehouse_id: UUID
    sku_id: UUID
    quantity_on_hand: float
    confidence_score: int = Field(default=100, ge=0, le=100)
    confidence_reasons: List[str] = Field(default_factory=list)
    last_movement_date: Optional[datetime] = None

class InventoryBalanceResponse(InventoryBalanceBase):
    id: UUID
    created_on: datetime
    updated_on: datetime
