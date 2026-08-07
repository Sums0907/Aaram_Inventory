from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.domains.masters.models.supplier import Supplier

class SupplierRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, supplier_id: UUID) -> Optional[Supplier]:
        result = await self.session.execute(select(Supplier).filter(Supplier.id == supplier_id))
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[Supplier], int]:
        count_result = await self.session.execute(select(func.count()).select_from(Supplier))
        total = count_result.scalar() or 0
        
        result = await self.session.execute(select(Supplier).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_by_gstin(self, gstin: str) -> Optional[Supplier]:
        result = await self.session.execute(select(Supplier).filter(Supplier.gstin == gstin))
        return result.scalars().first()

    async def create(self, supplier: Supplier) -> Supplier:
        self.session.add(supplier)
        await self.session.commit()
        await self.session.refresh(supplier)
        return supplier

    async def update(self, supplier: Supplier) -> Supplier:
        await self.session.commit()
        await self.session.refresh(supplier)
        return supplier

    async def delete(self, supplier: Supplier) -> None:
        await self.session.delete(supplier)
        await self.session.commit()
