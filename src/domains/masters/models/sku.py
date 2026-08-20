from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from src.foundation.database.models import BaseModel
from src.foundation.enums.status import GenericStatus

class SKUModel(BaseModel):
    __tablename__ = "skus"

    item_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    sku_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    shopdeck_sku_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    
    # Variant attributes that make this SKU unique
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pattern: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    material: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    thread_count: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Authoritative UOM for component-capable items
    uom_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("units_of_measure.id"), nullable=True)
    
    # Any other dynamic attributes
    attribute_values: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default={})
    
    barcode: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    
    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
    )
    
    # Relationships
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="skus")
    pricing: Mapped[Optional["PricingModel"]] = relationship("PricingModel", back_populates="sku", uselist=False, cascade="all, delete-orphan")
    packaging: Mapped[Optional["PackagingModel"]] = relationship("PackagingModel", back_populates="sku", uselist=False, cascade="all, delete-orphan")
    images: Mapped[List["ProductImageModel"]] = relationship("ProductImageModel", back_populates="sku", cascade="all, delete-orphan")
    uom: Mapped[Optional["UnitOfMeasureModel"]] = relationship("UnitOfMeasureModel")
