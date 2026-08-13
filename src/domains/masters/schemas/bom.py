from typing import List, Optional
from datetime import date
from uuid import UUID
from pydantic import Field
from src.foundation.validation.base import BaseSchema

class BOMItemBase(BaseSchema):
    component_item_id: UUID
    quantity: float = Field(..., gt=0)
    uom_id: Optional[UUID] = None
    wastage_percentage: float = Field(default=0.0, ge=0.0)
    tolerance_percentage: float = Field(default=0.0, ge=0.0)

class BOMItemCreate(BOMItemBase):
    pass

class BOMItemResponse(BOMItemBase):
    id: UUID

class BOMBase(BaseSchema):
    bom_number: str = Field(..., max_length=255)
    bom_name: Optional[str] = Field(None, max_length=255)
    target_item_id: UUID
    target_quantity: int = Field(default=1, gt=0)
    status: str = Field(default="DRAFT", max_length=50)
    version: int = Field(default=1, ge=1)
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

class BOMCreate(BOMBase):
    items: List[BOMItemCreate]

class BOMResponse(BOMBase):
    id: UUID
    items: List[BOMItemResponse]
