from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from src.foundation.database.models import BaseModel

class ImportJobModel(BaseModel):
    __tablename__ = "import_jobs"

    integration_id: Mapped[UUID] = mapped_column(ForeignKey("integrations.id"), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., CSV_UPLOAD, API_SYNC
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING") # PENDING, PROCESSING, COMPLETED, FAILED, PARTIAL_SUCCESS
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    import_file = relationship("ImportFileModel", backref="import_job", uselist=False, lazy="selectin")
