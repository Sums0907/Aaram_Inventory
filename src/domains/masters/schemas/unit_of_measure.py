from typing import Optional
import uuid
from datetime import datetime
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus

class UnitOfMeasureBase(BaseSchema):
    unit_name: str = Field(..., min_length=1, max_length=100, description="Full Unit Name")
    short_name: str = Field(..., min_length=1, max_length=20, description="Short Representation")
    description: Optional[str] = Field(None, max_length=255)

class UnitOfMeasureCreate(UnitOfMeasureBase):
    unit_code: str = Field(..., min_length=1, max_length=50, description="Unique Immutable Code")

class UnitOfMeasureUpdate(UnitOfMeasureBase):
    # Unit Code is immutable
    pass

class UnitOfMeasureResponse(UnitOfMeasureCreate):
    id: uuid.UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
