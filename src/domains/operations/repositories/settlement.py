from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.operations.models.settlement import SettlementModel
from src.domains.operations.schemas.settlement import SettlementCreate

class SettlementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_settlement(self, data: SettlementCreate, created_by: UUID) -> SettlementModel:
        settlement_dict = data.model_dump()
        settlement_dict["created_by"] = created_by
        settlement_dict["updated_by"] = created_by
        
        db_settlement = SettlementModel(**settlement_dict)
        self.session.add(db_settlement)
        await self.session.commit()
        await self.session.refresh(db_settlement)
        return db_settlement
        
    async def get_by_settlement_id(self, settlement_id: str) -> SettlementModel | None:
        stmt = select(SettlementModel).where(SettlementModel.settlement_id == settlement_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
