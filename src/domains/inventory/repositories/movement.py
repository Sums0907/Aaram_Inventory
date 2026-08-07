from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.schemas.movement import InventoryMovementCreate

class InventoryMovementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_movement(self, data: InventoryMovementCreate, created_by: UUID) -> InventoryMovementModel:
        movement_dict = data.model_dump()
        movement_dict["created_by"] = created_by
        movement_dict["updated_by"] = created_by
        
        db_movement = InventoryMovementModel(**movement_dict)
        self.session.add(db_movement)
        await self.session.commit()
        await self.session.refresh(db_movement)
        return db_movement
        
    async def get_by_movement_number(self, movement_number: str) -> Optional[InventoryMovementModel]:
        stmt = select(InventoryMovementModel).where(InventoryMovementModel.movement_number == movement_number)
        result = await self.session.execute(stmt)
        return result.scalars().first()
        
    async def get_balance(self, warehouse_id: UUID, sku_id: UUID) -> int:
        stmt = select(func.sum(InventoryMovementModel.quantity)).where(
            InventoryMovementModel.warehouse_id == warehouse_id,
            InventoryMovementModel.sku_id == sku_id,
            InventoryMovementModel.status == "POSTED"
        )
        result = await self.session.execute(stmt)
        balance = result.scalar()
        return int(balance) if balance is not None else 0

    async def get_movements_for_sku(self, sku_id: UUID) -> List[InventoryMovementModel]:
        stmt = (
            select(InventoryMovementModel)
            .where(
                InventoryMovementModel.sku_id == sku_id,
                InventoryMovementModel.status == "POSTED"
            )
            .order_by(InventoryMovementModel.posting_date.asc(), InventoryMovementModel.created_on.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_manual_adjustments_today_count(self) -> int:
        from datetime import date
        stmt = select(func.count(InventoryMovementModel.id)).where(
            InventoryMovementModel.movement_type == "MANUAL_ADJUSTMENT",
            InventoryMovementModel.movement_date == date.today()
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
