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
    expected_quantity: int
    actual_quantity: int
    difference: int
    status: ExceptionStatus = ExceptionStatus.OPEN
    resolution_notes: Optional[str] = None

class InventoryExceptionCreate(InventoryExceptionBase):
    pass

class InventoryExceptionResponse(InventoryExceptionBase):
    id: UUID
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
