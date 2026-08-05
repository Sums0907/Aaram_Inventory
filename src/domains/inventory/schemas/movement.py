from typing import Optional
from uuid import UUID
from pydantic import Field
from datetime import date, datetime
from src.foundation.validation.base import BaseSchema

class InventoryMovementBase(BaseSchema):
    movement_number: str = Field(..., max_length=255)
    movement_type: str = Field(..., max_length=100)
    movement_date: date
    posting_date: date
    status: str = Field(..., max_length=50)

    warehouse_id: UUID
    sku_id: UUID
    
    quantity: int
    unit_cost: float
    
    reference_type: str = Field(..., max_length=100)
    reference_number: str = Field(..., max_length=255)
    reference_id: UUID

class InventoryMovementCreate(InventoryMovementBase):
    pass

class InventoryMovementResponse(InventoryMovementBase):
    id: UUID
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
