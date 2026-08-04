from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum as SQLAlchemyEnum
from src.foundation.database.models import BaseModel
from src.foundation.enums.status import GenericStatus

class UnitOfMeasureModel(BaseModel):
    __tablename__ = "units_of_measure"

    unit_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    unit_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    short_name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    status: Mapped[GenericStatus] = mapped_column(
        SQLAlchemyEnum(GenericStatus, name="generic_status", create_type=False),
        nullable=False,
        default=GenericStatus.ACTIVE,
    )
