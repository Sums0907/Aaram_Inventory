from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer
from src.foundation.database.models import BaseModel

class ProductImageModel(BaseModel):
    __tablename__ = "product_images"

    sku_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Relationships
    sku: Mapped["SKUModel"] = relationship("SKUModel", back_populates="images")
