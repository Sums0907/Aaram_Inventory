from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import Field
from src.foundation.validation.base import BaseSchema

class SupplierBase(BaseSchema):
    name: str = Field(..., max_length=255)
    gstin: Optional[str] = Field(None, max_length=15)
    contact_number: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    remarks: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    name: Optional[str] = Field(None, max_length=255)

class SupplierResponse(SupplierBase):
    id: UUID
    created_on: datetime
    updated_on: datetime
