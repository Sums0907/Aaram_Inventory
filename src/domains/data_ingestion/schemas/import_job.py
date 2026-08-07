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
    file_path: Optional[str] = None

class ImportJobPreviewResponse(BaseSchema):
    report_date_min: Optional[str] = None
    report_date_max: Optional[str] = None
    total_orders: int = 0
    total_skus: int = 0
    units_sold: int = 0
    units_returned: int = 0
