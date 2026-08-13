from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime

class InventoryItemResponse(BaseModel):
    id: UUID
    name: str
    inventory_code: str
    type: str # Finished Goods, Raw Material, etc.

class ActivityReference(BaseModel):
    type: str
    number: str
    id: UUID

class ActivityResponse(BaseModel):
    id: UUID
    activity_type: str # e.g. PURCHASE_RECEIPT
    activity_name: str # e.g. Goods Received
    date: date
    inventory_item: InventoryItemResponse
    quantity: float
    balance_after_activity: Optional[float] = None
    reference: ActivityReference
    remarks: Optional[str] = None
    created_on: datetime

class ActivityListResponse(BaseModel):
    total_count: int
    items: List[ActivityResponse]
