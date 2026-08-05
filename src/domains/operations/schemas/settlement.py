from typing import Optional
from uuid import UUID
from pydantic import Field
from datetime import date, datetime
from src.foundation.validation.base import BaseSchema

class SettlementBase(BaseSchema):
    settlement_id: str = Field(..., max_length=255)
    cycle_date: str = Field(..., max_length=255)
    settlement_date: date
    status: str = Field(..., max_length=100)
    
    gross_amount: float = Field(..., ge=0)
    fees: float = Field(..., ge=0) # We might store fees as negative depending on convention, ge=0 might fail, let's remove ge=0 for fees and amounts in settlements
    net_amount: float = Field(...)
    
    utr_number: str = Field(..., max_length=255)
    bank_account: Optional[str] = Field(None, max_length=255)

class SettlementCreate(BaseSchema):
    settlement_id: str = Field(..., max_length=255)
    cycle_date: str = Field(..., max_length=255)
    settlement_date: date
    status: str = Field(..., max_length=100)
    
    gross_amount: float
    fees: float
    net_amount: float
    
    utr_number: str = Field(..., max_length=255)
    bank_account: Optional[str] = Field(None, max_length=255)

class SettlementResponse(SettlementCreate):
    id: UUID
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
