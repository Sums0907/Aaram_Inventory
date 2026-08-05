from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, DateTime, ForeignKey
from src.foundation.database.models import BaseModel

class PaymentModel(BaseModel):
    __tablename__ = "operations_payments"

    transaction_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    transaction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    order_reference: Mapped[str] = mapped_column(String(255), nullable=False, index=True) # E.g., order_receipt. Unmatched initially.
    matched_order_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("operations_sales_orders.id"), nullable=True, index=True)
    
    payment_method: Mapped[str] = mapped_column(String(100), nullable=False)
    
    gross_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    gateway_fee: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    gateway_tax: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    net_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    
    payment_captured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    settlement_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("operations_settlements.id"), nullable=True, index=True)
    external_settlement_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utr_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    settlement: Mapped[Optional["SettlementModel"]] = relationship("SettlementModel", back_populates="payments")
