from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Enum as SQLAlchemyEnum
from src.foundation.database.models import BaseModel
from src.foundation.enums.status import GenericStatus

class CompanyModel(BaseModel):
    __tablename__ = "companies"

    company_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    gstin: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    pan: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    mobile: Mapped[str] = mapped_column(String(50), nullable=True)
    website: Mapped[str] = mapped_column(String(255), nullable=True)
    
    address_line_1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line_2: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="India")
    pin_code: Mapped[str] = mapped_column(String(20), nullable=False)
    
    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
    )
