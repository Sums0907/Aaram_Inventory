from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from src.domains.inventory.models.purchase_return import PurchaseReturn

class PurchaseReturnRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, return_id: UUID) -> Optional[PurchaseReturn]:
        result = await self.session.execute(
            select(PurchaseReturn)
            .options(selectinload(PurchaseReturn.items))
            .filter(PurchaseReturn.id == return_id)
        )
        return result.scalars().first()

    async def get_by_return_number(self, return_number: str) -> Optional[PurchaseReturn]:
        result = await self.session.execute(
            select(PurchaseReturn)
            .options(selectinload(PurchaseReturn.items))
            .filter(PurchaseReturn.return_number == return_number)
        )
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[PurchaseReturn], int]:
        count_result = await self.session.execute(select(func.count()).select_from(PurchaseReturn))
        total = count_result.scalar() or 0
        
        result = await self.session.execute(
            select(PurchaseReturn)
            .options(selectinload(PurchaseReturn.items))
            .order_by(PurchaseReturn.created_on.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def create(self, purchase_return: PurchaseReturn) -> PurchaseReturn:
        self.session.add(purchase_return)
        await self.session.commit()
        # After commit, the object is expired. We re-fetch it with selectinload to ensure relationships are loaded and prevent MissingGreenlet errors.
        return await self.get_by_id(purchase_return.id)
