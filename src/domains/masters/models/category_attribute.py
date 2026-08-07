from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Boolean
from uuid import UUID
from src.foundation.database.models import BaseModel

class CategoryAttributeModel(BaseModel):
    __tablename__ = "category_attributes"

    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    attribute_id: Mapped[UUID] = mapped_column(ForeignKey("product_attributes.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    category: Mapped["CategoryModel"] = relationship("CategoryModel", back_populates="category_attributes")
    attribute: Mapped["ProductAttributeModel"] = relationship("ProductAttributeModel")
