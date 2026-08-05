from typing import Optional
import uuid
from datetime import datetime
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus

class ProductAttributeBase(BaseSchema):
    attribute_name: str = Field(..., min_length=1, max_length=100, description="Attribute Name")
    description: Optional[str] = Field(None, max_length=255)
    display_order: Optional[int] = Field(None, ge=0)

class ProductAttributeCreate(ProductAttributeBase):
    attribute_code: str = Field(..., min_length=1, max_length=50, description="Unique Immutable Code")

class ProductAttributeUpdate(ProductAttributeBase):
    # Attribute Code is immutable
    pass

class ProductAttributeResponse(ProductAttributeCreate):
    id: uuid.UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
