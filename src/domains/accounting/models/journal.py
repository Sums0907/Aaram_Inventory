from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Numeric, ForeignKey
from src.foundation.database.models import BaseModel

class JournalEntryModel(BaseModel):
    __tablename__ = "accounting_journal_entries"

    journal_number: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    journal_date: Mapped[date] = mapped_column(Date, nullable=False)
    posting_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # SYSTEM, MANUAL
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="SYSTEM")
    
    # e.g. SALES_ORDER, PAYMENT, SETTLEMENT, INVENTORY_MOVEMENT
    reference_type: Mapped[str] = mapped_column(String(100), nullable=False)
    reference_number: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="POSTED")
    narration: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    lines: Mapped[List["JournalLineModel"]] = relationship("JournalLineModel", back_populates="journal", cascade="all, delete-orphan")


class JournalLineModel(BaseModel):
    __tablename__ = "accounting_journal_lines"

    journal_id: Mapped[UUID] = mapped_column(ForeignKey("accounting_journal_entries.id"), nullable=False, index=True)
    ledger_id: Mapped[UUID] = mapped_column(ForeignKey("accounting_ledgers.id"), nullable=False, index=True)
    
    debit_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    credit_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    
    narration: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    journal: Mapped["JournalEntryModel"] = relationship("JournalEntryModel", back_populates="lines")
