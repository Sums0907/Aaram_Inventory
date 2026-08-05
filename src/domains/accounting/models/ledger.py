from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from src.foundation.database.models import BaseModel

class LedgerModel(BaseModel):
    __tablename__ = "accounting_ledgers"

    ledger_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    ledger_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
