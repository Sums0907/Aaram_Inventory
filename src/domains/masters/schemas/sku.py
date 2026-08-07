from typing import Optional, Dict, List
from datetime import datetime
from uuid import UUID
from pydantic import Field, BaseModel as PydanticBaseModel
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus

class ProductInfo(PydanticBaseModel):
    id: UUID
    product_code: str
    product_name: str
    brand: Optional[str] = None
    product_type: Optional[str] = None
    item_type: str = "FINISHED_GOODS"

class PricingInfo(PydanticBaseModel):
    selling_price: float
    mrp: float
    cost_price: float
    gst_percentage: float
    hsn_code: Optional[str] = None

class ImageInfo(PydanticBaseModel):
    image_url: str
    display_order: int

class SKUBase(BaseSchema):
    size: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=255)
    pattern: Optional[str] = Field(None, max_length=255)
    material: Optional[str] = Field(None, max_length=255)
    thread_count: Optional[str] = Field(None, max_length=50)
    attribute_values: Dict[str, str] = Field(default_factory=dict, description="Other attributes")
    barcode: Optional[str] = Field(None, max_length=100)

class SKUCreate(SKUBase):
    item_code: str = Field(..., min_length=1, max_length=50, description="Unique Internal Item Code")
    sku_code: Optional[str] = Field(None, min_length=1, max_length=50, description="SKU Code for Finished Goods")
    product_id: UUID = Field(..., description="Product Reference")

class SKUUpdate(SKUBase):
    pass

class SKUResponse(SKUCreate):
    id: UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    # Joined fields for the UI
    product: Optional[ProductInfo] = None
    pricing: Optional[PricingInfo] = None
    images: List[ImageInfo] = Field(default_factory=list)

