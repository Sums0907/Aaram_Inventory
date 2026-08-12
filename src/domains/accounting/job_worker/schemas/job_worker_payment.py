from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class JobWorkerPaymentCreate(BaseModel):
    job_worker_id: UUID
    payment_date: date
    amount: float = Field(..., gt=0)
    payment_account: Optional[str] = None
    payment_reference: Optional[str] = None
    notes: Optional[str] = None


class JobWorkerPaymentResponse(BaseModel):
    id: UUID
    reference: str
    job_worker_id: UUID
    payment_date: date
    amount: float
    payment_account: Optional[str]
    payment_reference: Optional[str]
    notes: Optional[str]
    status: str
    created_on: datetime

    class Config:
        from_attributes = True
