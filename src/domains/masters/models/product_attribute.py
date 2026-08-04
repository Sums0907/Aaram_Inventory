from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Enum as SQLAlchemyEnum
from src.foundation.database.models import BaseModel
from src.foundation.enums.status import GenericStatus

class ProductAttributeModel(BaseModel):
    __tablename__ = "product_attributes"

    attribute_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    attribute_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=True)
    
    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
    )
