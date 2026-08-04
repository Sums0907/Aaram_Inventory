from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.masters.models.warehouse import WarehouseModel

class WarehouseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, warehouse_id: UUID) -> Optional[WarehouseModel]:
        result = await self.session.execute(select(WarehouseModel).filter(WarehouseModel.id == warehouse_id))
        return result.scalars().first()

    async def get_by_code(self, warehouse_code: str) -> Optional[WarehouseModel]:
        result = await self.session.execute(select(WarehouseModel).filter(WarehouseModel.warehouse_code == warehouse_code))
        return result.scalars().first()
        
    async def get_by_name(self, warehouse_name: str) -> Optional[WarehouseModel]:
        result = await self.session.execute(select(WarehouseModel).filter(WarehouseModel.warehouse_name == warehouse_name))
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[WarehouseModel]:
        result = await self.session.execute(select(WarehouseModel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, warehouse: WarehouseModel) -> WarehouseModel:
        self.session.add(warehouse)
        await self.session.commit()
        await self.session.refresh(warehouse)
        return warehouse

    async def update(self, warehouse: WarehouseModel) -> WarehouseModel:
        await self.session.commit()
        await self.session.refresh(warehouse)
        return warehouse
