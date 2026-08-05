from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum as SQLAlchemyEnum
from src.foundation.database.models import BaseModel
from src.foundation.enums.status import GenericStatus

class IntegrationModel(BaseModel):
    __tablename__ = "integrations"

    integration_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    integration_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    integration_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. MARKETPLACE, ACCOUNTING
    
    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
    )
