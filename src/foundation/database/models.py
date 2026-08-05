import uuid
from uuid_extensions import uuid7
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Uuid
from datetime import datetime
from sqlalchemy import DateTime
from src.foundation.database.session import Base
from src.foundation.utilities.dates import utc_now

class BaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid7
    )
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=True)
    updated_by: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=True)
