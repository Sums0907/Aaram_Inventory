import uuid
from datetime import datetime
from typing import Optional
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus

class CategoryBase(BaseSchema):
    category_name: str = Field(..., min_length=1, max_length=100, description="Category Name")
    description: Optional[str] = Field(None, max_length=255)
    display_order: Optional[int] = Field(None, ge=0)
    parent_id: Optional[uuid.UUID] = Field(None, description="Parent Category ID for Subcategories")
    item_type: str = Field(default="FINISHED_GOODS", description="Inventory Item Type")

class CategoryCreate(CategoryBase):
    category_code: Optional[str] = Field(None, min_length=1, max_length=50, description="Unique Immutable Code")
    attributes: Optional[list[str]] = Field(default_factory=list, description="List of attribute names required for this category")

class CategoryUpdate(CategoryBase):
    attributes: Optional[list[str]] = Field(default_factory=list, description="List of attribute names required for this category")

class CategoryAttributeResponse(BaseSchema):
    attribute_name: str
    is_required: bool

    @classmethod
    def from_model(cls, attr_link):
        return cls(
            attribute_name=attr_link.attribute.attribute_name if attr_link.attribute else "",
            is_required=attr_link.is_required
        )

class CategoryResponse(CategoryBase):
    category_code: str
    id: uuid.UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    attributes: list[CategoryAttributeResponse] = Field(default_factory=list)

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if hasattr(obj, "category_attributes"):
            # Set the attributes list from the SQLAlchemy relationship
            attributes = [CategoryAttributeResponse.from_model(a) for a in obj.category_attributes]
            # Since obj is a SQLAlchemy model, we can't easily mutate it before validation,
            # so we'll let Pydantic validate it, then attach the attributes.
            res = super().model_validate(obj, *args, **kwargs)
            res.attributes = attributes
            return res
        return super().model_validate(obj, *args, **kwargs)
