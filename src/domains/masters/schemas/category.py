from typing import Optional
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus

class CategoryBase(BaseSchema):
    category_name: str = Field(..., min_length=1, max_length=100, description="Category Name")
    description: Optional[str] = Field(None, max_length=255)
    display_order: Optional[int] = Field(None, ge=0)

class CategoryCreate(CategoryBase):
    category_code: str = Field(..., min_length=1, max_length=50, description="Unique Immutable Code")

class CategoryUpdate(CategoryBase):
    # Category Code is immutable
    pass

class CategoryResponse(CategoryCreate):
    import uuid
    from datetime import datetime
    
    id: uuid.UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
