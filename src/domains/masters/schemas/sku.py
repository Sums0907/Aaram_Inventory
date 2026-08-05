from typing import Optional, Dict
from datetime import datetime
from uuid import UUID
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus

class SKUBase(BaseSchema):
    sku_name: str = Field(..., min_length=1, max_length=100, description="SKU Name")
    attribute_values: Dict[str, str] = Field(default_factory=dict, description="Map of Attribute IDs to Values")
    barcode: Optional[str] = Field(None, max_length=100)
    hsn_code: Optional[str] = Field(None, max_length=20)
    gst_rate: float = Field(..., ge=0, le=100, description="GST Rate Percentage")

class SKUCreate(SKUBase):
    sku_code: str = Field(..., min_length=1, max_length=50, description="Unique Immutable Code")
    inventory_item_id: UUID = Field(..., description="Inventory Item Reference")

class SKUUpdate(SKUBase):
    # SKU Code and Inventory Item are immutable
    pass

class SKUResponse(SKUCreate):
    id: UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
