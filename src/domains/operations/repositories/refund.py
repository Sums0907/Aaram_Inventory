from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.operations.models.refund import RefundModel
from src.domains.operations.schemas.refund import RefundCreate

class RefundRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_refund(self, data: RefundCreate, created_by: UUID) -> RefundModel:
        refund_dict = data.model_dump()
        refund_dict["created_by"] = created_by
        refund_dict["updated_by"] = created_by
        
        db_refund = RefundModel(**refund_dict)
        self.session.add(db_refund)
        await self.session.commit()
        await self.session.refresh(db_refund)
        return db_refund
        
    async def get_by_transaction_id(self, transaction_id: str) -> RefundModel | None:
        stmt = select(RefundModel).where(RefundModel.transaction_id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
