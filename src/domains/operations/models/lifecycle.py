from datetime import date, datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, DateTime, Boolean, ForeignKey, UniqueConstraint
from src.foundation.database.models import BaseModel
from uuid import UUID

class CustomerReturnPolicyModel(BaseModel):
    __tablename__ = "operations_return_policies"

    effective_from: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    return_window_days: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class OrderStateTransitionModel(BaseModel):
    __tablename__ = "operations_order_state_transitions"
    
    order_id: Mapped[UUID] = mapped_column(ForeignKey("operations_sales_orders.id"), nullable=False, index=True)
    external_order_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    old_status: Mapped[str] = mapped_column(String(100), nullable=True)
    new_status: Mapped[str] = mapped_column(String(100), nullable=False)
    
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=True)
    source_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    transition_type: Mapped[str] = mapped_column(String(50), nullable=False, default="STATE_TRANSITION")

    __table_args__ = (
        UniqueConstraint('external_order_id', 'new_status', 'observed_at', name='uix_order_transition_idempotency'),
    )
