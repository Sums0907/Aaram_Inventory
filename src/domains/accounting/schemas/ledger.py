from typing import Optional
from uuid import UUID
from pydantic import Field
from datetime import datetime
from src.foundation.validation.base import BaseSchema

class LedgerBase(BaseSchema):
    ledger_code: str = Field(..., max_length=100)
    ledger_name: str = Field(..., max_length=255)
    account_type: str = Field(..., max_length=50)
    is_active: bool = True
    description: Optional[str] = Field(None, max_length=500)

class LedgerCreate(LedgerBase):
    pass

class LedgerResponse(LedgerBase):
    id: UUID
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
