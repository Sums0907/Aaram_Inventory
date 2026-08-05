from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import Field
from src.foundation.validation.base import BaseSchema

class ImportJobBase(BaseSchema):
    integration_id: UUID
    job_type: str = Field(..., max_length=50)

class ImportJobCreate(ImportJobBase):
    status: str = Field("PENDING", max_length=50)

class ImportJobUpdate(BaseSchema):
    status: Optional[str] = Field(None, max_length=50)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

class ImportJobResponse(ImportJobCreate):
    id: UUID
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
