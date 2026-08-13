from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from src.domains.inventory.schemas.enums import ExceptionSource, ExceptionStatus

class InventoryExceptionBase(BaseSchema):
    exception_number: str = Field(..., max_length=255)
    warehouse_id: UUID
    sku_id: UUID
    exception_date: datetime
    source_system: ExceptionSource
    expected_quantity: float
    actual_quantity: float
    difference: float
    status: ExceptionStatus = ExceptionStatus.OPEN
    resolution_notes: Optional[str] = None

class InventoryExceptionCreate(InventoryExceptionBase):
    pass

class InventoryExceptionResponse(InventoryExceptionBase):
    id: UUID
    created_on: datetime
    updated_on: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
class ExceptionInventoryItem(BaseSchema):
    inventory_code: str
    name: str

class EnrichedExceptionResponse(InventoryExceptionResponse):
    inventory_item: ExceptionInventoryItem

class ExceptionListResponse(BaseSchema):
    total_count: int
    items: list[EnrichedExceptionResponse]

class ResolveExceptionRequest(BaseSchema):
    resolution_notes: str
