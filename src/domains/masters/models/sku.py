from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Numeric, Enum as SQLAlchemyEnum
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from src.foundation.database.models import BaseModel
from src.foundation.enums.status import GenericStatus

class SKUModel(BaseModel):
    __tablename__ = "skus"

    sku_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    sku_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    inventory_item_id: Mapped[UUID] = mapped_column(ForeignKey("inventory_items.id"), nullable=False)
    
    attribute_values: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default={})
    
    barcode: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    hsn_code: Mapped[str] = mapped_column(String(20), nullable=True)
    gst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    
    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
    )
