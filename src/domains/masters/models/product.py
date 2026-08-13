from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Table, Column
from src.foundation.database.models import BaseModel
from sqlalchemy import Enum as SQLAlchemyEnum
from src.foundation.enums import ItemType, GenericStatus

# Association table for Products and Product Attributes
product_attributes_table = Table(
    "product_attributes_link",
    BaseModel.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("product_attribute_id", ForeignKey("product_attributes.id"), primary_key=True),
)

class ProductModel(BaseModel):
    __tablename__ = "products"

    product_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    product_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    item_type: Mapped[ItemType] = mapped_column(
        SQLAlchemyEnum(ItemType, name="item_type_enum", create_type=False),
        nullable=False,
        default=ItemType.FINISHED_GOODS,
        server_default="FINISHED_GOODS"
    )

    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status_enum", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
        server_default="ACTIVE"
    )
    
    # We may still link to categories later, but making it nullable for now since CSV might not perfectly align with existing categories
    category_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    
    # Relationships
    skus: Mapped[List["SKUModel"]] = relationship("SKUModel", back_populates="product", cascade="all, delete-orphan")
    
    attributes: Mapped[List["ProductAttributeModel"]] = relationship(
        "ProductAttributeModel",
        secondary=product_attributes_table,
        lazy="selectin"
    )
