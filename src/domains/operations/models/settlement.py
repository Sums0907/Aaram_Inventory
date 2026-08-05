from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Numeric, ForeignKey
from src.foundation.database.models import BaseModel

class SettlementModel(BaseModel):
    __tablename__ = "operations_settlements"

    settlement_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    cycle_date: Mapped[str] = mapped_column(String(255), nullable=False)
    settlement_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    
    gross_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    fees: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    net_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    
    utr_number: Mapped[str] = mapped_column(String(255), nullable=False)
    bank_account: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    payments: Mapped[List["PaymentModel"]] = relationship("PaymentModel", back_populates="settlement")
