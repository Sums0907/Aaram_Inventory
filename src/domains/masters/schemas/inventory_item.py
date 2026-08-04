from typing import Optional, List
from uuid import UUID
from pydantic import Field, validator
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus

class InventoryItemBase(BaseSchema):
    item_name: str = Field(..., min_length=1, max_length=100, description="Item Name")
    description: Optional[str] = Field(None, max_length=255)
    category_id: UUID = Field(..., description="Category Reference")
    unit_of_measure_id: UUID = Field(..., description="UoM Reference")
    product_attribute_ids: Optional[List[UUID]] = Field(default_factory=list, description="Product Attributes References")
    hsn_code: Optional[str] = Field(None, max_length=20)
    gst_rate: float = Field(..., ge=0, le=100, description="GST Rate Percentage")

class InventoryItemCreate(InventoryItemBase):
    item_code: str = Field(..., min_length=1, max_length=50, description="Unique Immutable Code")

class InventoryItemUpdate(InventoryItemBase):
    # Item Code is immutable
    pass

class InventoryItemResponse(InventoryItemCreate):
    from datetime import datetime
    
    id: UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
