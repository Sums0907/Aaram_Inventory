from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel

class UnitOfMeasureRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, unit_id: UUID) -> Optional[UnitOfMeasureModel]:
        result = await self.session.execute(select(UnitOfMeasureModel).filter(UnitOfMeasureModel.id == unit_id))
        return result.scalars().first()

    async def get_by_code(self, unit_code: str) -> Optional[UnitOfMeasureModel]:
        result = await self.session.execute(select(UnitOfMeasureModel).filter(UnitOfMeasureModel.unit_code == unit_code))
        return result.scalars().first()
        
    async def get_by_name(self, unit_name: str) -> Optional[UnitOfMeasureModel]:
        result = await self.session.execute(select(UnitOfMeasureModel).filter(UnitOfMeasureModel.unit_name == unit_name))
        return result.scalars().first()
        
    async def get_by_short_name(self, short_name: str) -> Optional[UnitOfMeasureModel]:
        result = await self.session.execute(select(UnitOfMeasureModel).filter(UnitOfMeasureModel.short_name == short_name))
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UnitOfMeasureModel]:
        result = await self.session.execute(select(UnitOfMeasureModel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, unit: UnitOfMeasureModel) -> UnitOfMeasureModel:
        self.session.add(unit)
        await self.session.commit()
        await self.session.refresh(unit)
        return unit

    async def update(self, unit: UnitOfMeasureModel) -> UnitOfMeasureModel:
        await self.session.commit()
        await self.session.refresh(unit)
        return unit
