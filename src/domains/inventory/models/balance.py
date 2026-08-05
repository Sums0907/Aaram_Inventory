from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, JSON
from src.foundation.database.models import BaseModel

class InventoryBalanceModel(BaseModel):
    __tablename__ = "inventory_balances"
    __table_args__ = (
        UniqueConstraint('warehouse_id', 'sku_id', name='uq_inventory_balance_warehouse_sku'),
    )

    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    sku_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    
    quantity_on_hand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Confidence tracking
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100) # 0 to 100
    confidence_reasons: Mapped[dict] = mapped_column(JSON, nullable=False, default=list) # List of strings explaining the score
    
    last_movement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
