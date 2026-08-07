from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from pydantic import Field
from src.foundation.validation.base import BaseSchema

class PurchaseReturnItemBase(BaseSchema):
    sku_id: UUID
    quantity: int = Field(..., gt=0)
    unit_of_measure: Optional[str] = None

class PurchaseReturnItemCreate(PurchaseReturnItemBase):
    pass

class PurchaseReturnItemResponse(PurchaseReturnItemBase):
    id: UUID

class PurchaseReturnBase(BaseSchema):
    supplier_id: UUID
    warehouse_id: UUID
    return_date: date
    reference_grn: Optional[str] = None
    remarks: Optional[str] = None

class PurchaseReturnCreate(PurchaseReturnBase):
    return_number: str = Field(..., max_length=255)
    items: List[PurchaseReturnItemCreate] = Field(..., min_length=1)

class PurchaseReturnResponse(PurchaseReturnBase):
    id: UUID
    return_number: str
    status: str
    created_on: datetime
    updated_on: datetime
    items: List[PurchaseReturnItemResponse]
