from uuid import UUID
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.accounting.models.ledger import LedgerModel
from src.domains.accounting.schemas.ledger import LedgerCreate

class LedgerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_ledger(self, data: LedgerCreate, created_by: UUID) -> LedgerModel:
        ledger_dict = data.model_dump()
        ledger_dict["created_by"] = created_by
        ledger_dict["updated_by"] = created_by
        
        db_ledger = LedgerModel(**ledger_dict)
        self.session.add(db_ledger)
        await self.session.commit()
        await self.session.refresh(db_ledger)
        return db_ledger
        
    async def get_by_code(self, ledger_code: str) -> Optional[LedgerModel]:
        stmt = select(LedgerModel).where(LedgerModel.ledger_code == ledger_code)
        result = await self.session.execute(stmt)
        return result.scalars().first()
