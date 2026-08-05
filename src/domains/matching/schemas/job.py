from datetime import datetime
from uuid import UUID
from typing import Optional
from src.foundation.validation.base import BaseSchema

class MatchJobCreate(BaseSchema):
    started_on: datetime
    status: str = "RUNNING"
    orders_processed: int = 0
    payments_processed: int = 0
    settlements_processed: int = 0
    invoices_processed: int = 0
    successful_matches: int = 0
    failed_matches: int = 0
    exceptions_generated: int = 0

class MatchJobUpdate(BaseSchema):
    completed_on: Optional[datetime] = None
    status: Optional[str] = None
    orders_processed: Optional[int] = None
    payments_processed: Optional[int] = None
    settlements_processed: Optional[int] = None
    invoices_processed: Optional[int] = None
    successful_matches: Optional[int] = None
    failed_matches: Optional[int] = None
    exceptions_generated: Optional[int] = None

class MatchJobResponse(MatchJobCreate):
    id: UUID
    completed_on: Optional[datetime] = None
