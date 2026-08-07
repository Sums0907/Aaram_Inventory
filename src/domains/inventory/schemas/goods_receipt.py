from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from pydantic import Field
from src.foundation.validation.base import BaseSchema

class GoodsReceiptItemBase(BaseSchema):
    sku_id: UUID
    quantity: int = Field(..., gt=0)
    unit_of_measure: Optional[str] = None

class GoodsReceiptItemCreate(GoodsReceiptItemBase):
    pass

class GoodsReceiptItemResponse(GoodsReceiptItemBase):
    id: UUID

class GoodsReceiptBase(BaseSchema):
    supplier_id: UUID
    warehouse_id: UUID
    receipt_date: date
    invoice_number: Optional[str] = None
    challan_number: Optional[str] = None
    remarks: Optional[str] = None

class GoodsReceiptCreate(GoodsReceiptBase):
    grn_number: str = Field(..., max_length=255)
    items: List[GoodsReceiptItemCreate] = Field(..., min_length=1)

class GoodsReceiptResponse(GoodsReceiptBase):
    id: UUID
    grn_number: str
    status: str
    created_on: datetime
    updated_on: datetime
    items: List[GoodsReceiptItemResponse]
