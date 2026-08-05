import uuid
from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus
from src.foundation.constants.regex import EMAIL_REGEX

class WarehouseBase(BaseSchema):
    warehouse_name: str = Field(..., min_length=1, max_length=100, description="Full Warehouse Name")
    description: Optional[str] = Field(None, max_length=255)
    
    address_line_1: str = Field(..., min_length=1, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    country: str = Field("India", min_length=1, max_length=100)
    pin_code: str = Field(..., min_length=1, max_length=20)
    
    contact_person: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)

    @field_validator("email")
    def validate_email(cls, v):
        if v and not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

class WarehouseCreate(WarehouseBase):
    warehouse_code: str = Field(..., min_length=1, max_length=50, description="Unique Immutable Code")

class WarehouseUpdate(WarehouseBase):
    # Warehouse Code is immutable
    pass

class WarehouseResponse(WarehouseCreate):
    id: uuid.UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
