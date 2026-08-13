from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus
from src.foundation.enums import ItemType

class ProductBase(BaseSchema):
    product_name: str = Field(..., min_length=1, max_length=150, description="Product Name")
    description: Optional[str] = Field(None, max_length=5000)
    brand: Optional[str] = Field(None, max_length=100)
    product_type: Optional[str] = Field(None, max_length=100)
    item_type: ItemType = Field(default=ItemType.FINISHED_GOODS, description="Item Type")
    category_id: Optional[UUID] = Field(None, description="Category Reference")
    product_attribute_ids: Optional[List[UUID]] = Field(default_factory=list, description="Product Attributes References")

class ProductCreate(ProductBase):
    product_code: str = Field(..., min_length=1, max_length=50, description="Unique Immutable Code")

class ProductUpdate(ProductBase):
    # Product Code is immutable
    pass

class ProductResponse(ProductCreate):
    id: UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    has_bom: bool = Field(default=False)
