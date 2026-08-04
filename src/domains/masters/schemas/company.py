from typing import Optional
from pydantic import Field, field_validator, model_validator
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus
from src.foundation.constants.regex import EMAIL_REGEX
import re

# Simple regex for PAN (10 chars: 5 letters, 4 numbers, 1 letter)
PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
# Simple regex for GSTIN (15 chars)
GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

class CompanyBase(BaseSchema):
    company_name: str = Field(..., min_length=1, max_length=255, description="Official Company Name")
    legal_name: str = Field(..., min_length=1, max_length=255, description="Legal Name")
    display_name: Optional[str] = Field(None, max_length=255)
    
    gstin: str = Field(..., min_length=15, max_length=15)
    pan: str = Field(..., min_length=10, max_length=10)
    
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    
    address_line_1: str = Field(..., min_length=1, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    country: str = Field("India", min_length=1, max_length=100)
    pin_code: str = Field(..., min_length=1, max_length=20)

    @field_validator("pan")
    def validate_pan(cls, v):
        if not PAN_REGEX.match(v.upper()):
            raise ValueError("Invalid PAN format")
        return v.upper()

    @field_validator("gstin")
    def validate_gstin(cls, v):
        if not GSTIN_REGEX.match(v.upper()):
            raise ValueError("Invalid GSTIN format")
        return v.upper()
        
    @field_validator("email")
    def validate_email(cls, v):
        if v and not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v
        
    @model_validator(mode='after')
    def set_display_name(self):
        if not self.display_name:
            self.display_name = self.company_name
        return self

class CompanyCreate(CompanyBase):
    company_code: str = Field(..., min_length=1, max_length=50, description="Unique Company Code")

class CompanyUpdate(CompanyBase):
    # Company Code is immutable, so it is absent in the Update schema
    pass

class CompanyResponse(CompanyCreate):
    import uuid
    from datetime import datetime
    
    id: uuid.UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
