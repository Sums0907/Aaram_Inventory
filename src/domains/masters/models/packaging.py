from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Numeric
from src.foundation.database.models import BaseModel

class PackagingModel(BaseModel):
    __tablename__ = "packaging"

    sku_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), unique=True, nullable=False)
    
    length: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    breadth: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    height: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    
    package_contents: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    sku: Mapped["SKUModel"] = relationship("SKUModel", back_populates="packaging")
