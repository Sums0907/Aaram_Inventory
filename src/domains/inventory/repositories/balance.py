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

    async def get_dashboard_kpis(self) -> dict:
        from sqlalchemy import func
        # total skus
        stmt_skus = select(func.count(InventoryBalanceModel.id))
        total_skus = await self.session.execute(stmt_skus)
        total_skus = total_skus.scalar() or 0
        
        # total negative inventory skus
        stmt_neg = select(func.count(InventoryBalanceModel.id)).where(InventoryBalanceModel.quantity_on_hand < 0)
        total_negative = await self.session.execute(stmt_neg)
        total_negative = total_negative.scalar() or 0
        
        # average confidence
        stmt_conf = select(func.avg(InventoryBalanceModel.confidence_score))
        avg_conf = await self.session.execute(stmt_conf)
        avg_conf = avg_conf.scalar() or 0
        
        return {
            "total_skus_tracked": total_skus,
            "total_negative_inventory": total_negative,
            "average_confidence_score": round(avg_conf, 2)
        }
