from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum as SQLAlchemyEnum
from src.foundation.database.models import BaseModel
from src.foundation.enums.status import GenericStatus

class WarehouseModel(BaseModel):
    __tablename__ = "warehouses"

    warehouse_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    warehouse_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    address_line_1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line_2: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="India")
    pin_code: Mapped[str] = mapped_column(String(20), nullable=False)
    
    contact_person: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    
    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
    )
