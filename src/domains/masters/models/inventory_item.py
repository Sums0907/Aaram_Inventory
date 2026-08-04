from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Numeric, Enum as SQLAlchemyEnum, Table, Column
from src.foundation.database.models import BaseModel
from src.foundation.enums.status import GenericStatus

# Association table for Inventory Items and Product Attributes
inventory_item_attributes_table = Table(
    "inventory_item_attributes",
    BaseModel.metadata,
    Column("inventory_item_id", ForeignKey("inventory_items.id"), primary_key=True),
    Column("product_attribute_id", ForeignKey("product_attributes.id"), primary_key=True),
)

class InventoryItemModel(BaseModel):
    __tablename__ = "inventory_items"

    item_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)
    unit_of_measure_id: Mapped[UUID] = mapped_column(ForeignKey("units_of_measure.id"), nullable=False)
    
    hsn_code: Mapped[str] = mapped_column(String(20), nullable=True)
    gst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    
    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
    )

    # Relationships
    product_attributes: Mapped[List["ProductAttributeModel"]] = relationship(
        "ProductAttributeModel",
        secondary=inventory_item_attributes_table,
        lazy="selectin"
    )
