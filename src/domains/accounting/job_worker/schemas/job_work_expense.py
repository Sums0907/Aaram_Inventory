from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class JobWorkExpenseCreate(BaseModel):
    """Manually create an expense (e.g. for correction / manual entry)."""
    job_worker_id: UUID
    finished_product_id: UUID
    quantity: float = Field(..., gt=0)
    rate: float = Field(..., gt=0)
    rate_basis: str = "PER_PIECE"
    expense_date: date
    source_receipt_id: Optional[UUID] = None
    source_receipt_number: Optional[str] = None
    notes: Optional[str] = None


class JobWorkExpenseResponse(BaseModel):
    id: UUID
    reference: str
    job_worker_id: UUID
    finished_product_id: UUID
    quantity: float
    rate: float
    rate_basis: str
    amount: float
    source_receipt_id: Optional[UUID]
    source_receipt_number: Optional[str]
    expense_date: date
    status: str
    notes: Optional[str]
    created_on: datetime

    class Config:
        from_attributes = True
