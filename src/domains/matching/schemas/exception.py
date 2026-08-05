from uuid import UUID
from typing import Optional
from datetime import datetime
from src.foundation.validation.base import BaseSchema

class MatchExceptionCreate(BaseSchema):
    match_job_id: UUID
    document_type: str
    document_id: UUID
    reason: str
    status: str = "OPEN"

class MatchExceptionUpdate(BaseSchema):
    status: Optional[str] = None

class MatchExceptionResponse(MatchExceptionCreate):
    id: UUID
    created_on: datetime
    updated_on: datetime
