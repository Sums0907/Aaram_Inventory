from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum as SQLAlchemyEnum, ForeignKey
from src.foundation.database.models import BaseModel
from typing import Optional, List
from uuid import UUID
from src.foundation.enums.status import GenericStatus
from src.foundation.enums import ItemType

class CategoryModel(BaseModel):
    __tablename__ = "categories"

    category_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    category_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    display_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    parent_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    
    item_type: Mapped[ItemType] = mapped_column(
        SQLAlchemyEnum(ItemType, name="item_type_enum", create_type=False),
        nullable=False,
        default=ItemType.FINISHED_GOODS,
        server_default="FINISHED_GOODS"
    )
    
    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
    )
    
    # Relationships
    children: Mapped[List["CategoryModel"]] = relationship(
        "CategoryModel", 
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    parent: Mapped[Optional["CategoryModel"]] = relationship(
        "CategoryModel",
        back_populates="children",
        remote_side="CategoryModel.id"
    )
    
    category_attributes: Mapped[List["CategoryAttributeModel"]] = relationship(
        "CategoryAttributeModel",
        back_populates="category",
        cascade="all, delete-orphan"
    )
