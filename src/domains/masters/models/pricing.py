from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Numeric
from src.foundation.database.models import BaseModel

class PricingModel(BaseModel):
    __tablename__ = "pricing"

    sku_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), unique=True, nullable=False)
    
    selling_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    mrp: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cost_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    gst_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    hsn_code: Mapped[str] = mapped_column(String(20), nullable=True)
    
    # Relationships
    sku: Mapped["SKUModel"] = relationship("SKUModel", back_populates="pricing")
