from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from src.foundation.database.models import BaseModel

class MatchExceptionModel(BaseModel):
    __tablename__ = "matching_exceptions"

    match_job_id: Mapped[UUID] = mapped_column(ForeignKey("matching_jobs.id"), nullable=False, index=True)
    
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    document_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN") # OPEN, RESOLVED
