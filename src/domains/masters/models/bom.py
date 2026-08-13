from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Numeric, Date
from src.foundation.database.models import BaseModel
from typing import List

class BOMModel(BaseModel):
    __tablename__ = "masters_boms"

    bom_number: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    bom_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_item_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    target_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    
    # BOM v2.0 Extensions
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    effective_from: Mapped[str] = mapped_column(Date, nullable=True)
    effective_to: Mapped[str] = mapped_column(Date, nullable=True)

    # Relationships
    items: Mapped[List["BOMItemModel"]] = relationship("BOMItemModel", back_populates="bom", cascade="all, delete-orphan")


class BOMItemModel(BaseModel):
    __tablename__ = "masters_bom_items"

    bom_id: Mapped[UUID] = mapped_column(ForeignKey("masters_boms.id"), nullable=False, index=True)
    component_item_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    uom_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("units_of_measure.id"), nullable=True, index=True)
    unit_of_measure: Mapped[str] = mapped_column(String(50), nullable=False, default="-")
    
    # BOM v2.0 Extensions
    wastage_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    tolerance_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)

    # Relationships
    bom: Mapped["BOMModel"] = relationship("BOMModel", back_populates="items")
    uom: Mapped[Optional["UnitOfMeasureModel"]] = relationship("UnitOfMeasureModel")
