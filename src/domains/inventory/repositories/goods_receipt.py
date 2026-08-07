from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from src.domains.inventory.models.goods_receipt import GoodsReceipt

class GoodsReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, grn_id: UUID) -> Optional[GoodsReceipt]:
        result = await self.session.execute(
            select(GoodsReceipt)
            .options(selectinload(GoodsReceipt.items))
            .filter(GoodsReceipt.id == grn_id)
        )
        return result.scalars().first()

    async def get_by_grn_number(self, grn_number: str) -> Optional[GoodsReceipt]:
        result = await self.session.execute(
            select(GoodsReceipt)
            .options(selectinload(GoodsReceipt.items))
            .filter(GoodsReceipt.grn_number == grn_number)
        )
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[GoodsReceipt], int]:
        count_result = await self.session.execute(select(func.count()).select_from(GoodsReceipt))
        total = count_result.scalar() or 0
        
        result = await self.session.execute(
            select(GoodsReceipt)
            .options(selectinload(GoodsReceipt.items))
            .order_by(GoodsReceipt.created_on.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def create(self, grn: GoodsReceipt) -> GoodsReceipt:
        self.session.add(grn)
        await self.session.commit()
        # After commit, the object is expired. We re-fetch it with selectinload to ensure relationships are loaded and prevent MissingGreenlet errors.
        return await self.get_by_id(grn.id)
