from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class JobWorkRateCreate(BaseModel):
    job_worker_id: UUID
    sku_id: UUID
    rate: float = Field(..., gt=0)
    rate_basis: str = "PER_PIECE"
    effective_from: date
    notes: Optional[str] = None


class JobWorkRateUpdate(BaseModel):
    rate: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class JobWorkRateResponse(BaseModel):
    id: UUID
    job_worker_id: UUID
    sku_id: UUID
    rate: float
    rate_basis: str
    effective_from: date
    is_active: bool
    notes: Optional[str]
    created_on: datetime

    class Config:
        from_attributes = True
