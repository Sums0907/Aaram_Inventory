from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.inventory.models.exception import InventoryExceptionModel

class InventoryExceptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_number(self, exception_number: str) -> Optional[InventoryExceptionModel]:
        stmt = select(InventoryExceptionModel).where(InventoryExceptionModel.exception_number == exception_number)
        result = await self.session.execute(stmt)
        return result.scalars().first()
        
    async def get_open_exceptions_for_sku(self, sku_id: UUID) -> List[InventoryExceptionModel]:
        stmt = select(InventoryExceptionModel).where(
            InventoryExceptionModel.sku_id == sku_id,
            InventoryExceptionModel.status == "OPEN"
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_open_exceptions(self, limit: int = 50) -> List[InventoryExceptionModel]:
        stmt = select(InventoryExceptionModel).where(
            InventoryExceptionModel.status == "OPEN"
        ).order_by(InventoryExceptionModel.exception_date.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def save(self, exception: InventoryExceptionModel) -> InventoryExceptionModel:
        self.session.add(exception)
        await self.session.commit()
        await self.session.refresh(exception)
        return exception
