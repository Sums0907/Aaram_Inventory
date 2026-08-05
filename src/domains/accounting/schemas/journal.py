from typing import Optional, List
from uuid import UUID
from pydantic import Field, model_validator
from datetime import date, datetime
from src.foundation.validation.base import BaseSchema

class JournalLineBase(BaseSchema):
    ledger_id: UUID
    debit_amount: float = Field(0.0, ge=0)
    credit_amount: float = Field(0.0, ge=0)
    narration: Optional[str] = Field(None, max_length=1000)

class JournalLineCreate(JournalLineBase):
    @model_validator(mode='after')
    def check_amount(self):
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError("A line cannot have both debit and credit amounts")
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError("A line must have either a debit or credit amount")
        return self

class JournalLineResponse(JournalLineBase):
    id: UUID
    journal_id: UUID
    created_on: datetime
    updated_on: datetime

class JournalEntryBase(BaseSchema):
    journal_number: str = Field(..., max_length=255)
    journal_date: date
    posting_date: date
    source: str = Field(..., max_length=50)
    reference_type: str = Field(..., max_length=100)
    reference_number: str = Field(..., max_length=255)
    reference_id: UUID
    status: str = Field(..., max_length=50)
    narration: Optional[str] = Field(None, max_length=1000)

class JournalEntryCreate(JournalEntryBase):
    lines: List[JournalLineCreate]
    
    @model_validator(mode='after')
    def check_balance(self):
        total_debit = sum(line.debit_amount for line in self.lines)
        total_credit = sum(line.credit_amount for line in self.lines)
        if round(total_debit, 2) != round(total_credit, 2):
            raise ValueError(f"Journal must balance. Debits: {total_debit}, Credits: {total_credit}")
        return self

class JournalEntryResponse(JournalEntryBase):
    id: UUID
    lines: List[JournalLineResponse]
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
