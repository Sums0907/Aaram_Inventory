from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Date
from src.foundation.database.models import BaseModel

class DownloadedReportModel(BaseModel):
    __tablename__ = "shopdeck_downloaded_reports"

    source: Mapped[str] = mapped_column(String(100), nullable=False)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    period_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    period_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    downloaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    checksum: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., DOWNLOADED, IMPORTED, FAILED, DUPLICATE
    sync_run_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
