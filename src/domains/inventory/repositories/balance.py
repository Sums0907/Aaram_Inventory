from uuid import UUID
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.inventory.models.balance import InventoryBalanceModel

class InventoryBalanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_balance(self, warehouse_id: UUID, sku_id: UUID) -> Optional[InventoryBalanceModel]:
        stmt = select(InventoryBalanceModel).where(
            InventoryBalanceModel.warehouse_id == warehouse_id,
            InventoryBalanceModel.sku_id == sku_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
        
    async def save(self, balance: InventoryBalanceModel) -> InventoryBalanceModel:
        self.session.add(balance)
        await self.session.commit()
        await self.session.refresh(balance)
        return balance
