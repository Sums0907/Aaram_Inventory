from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from src.foundation.database.models import BaseModel

class MatchJobModel(BaseModel):
    __tablename__ = "matching_jobs"
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="RUNNING")
    started_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_on: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    orders_processed: Mapped[int] = mapped_column(Integer, default=0)
    payments_processed: Mapped[int] = mapped_column(Integer, default=0)
    settlements_processed: Mapped[int] = mapped_column(Integer, default=0)
    invoices_processed: Mapped[int] = mapped_column(Integer, default=0)
    
    successful_matches: Mapped[int] = mapped_column(Integer, default=0)
    failed_matches: Mapped[int] = mapped_column(Integer, default=0)
    exceptions_generated: Mapped[int] = mapped_column(Integer, default=0)
