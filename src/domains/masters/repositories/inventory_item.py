from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.masters.models.inventory_item import InventoryItemModel
from src.domains.masters.models.product_attribute import ProductAttributeModel

class InventoryItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, item_id: UUID) -> Optional[InventoryItemModel]:
        result = await self.session.execute(
            select(InventoryItemModel)
            .options(selectinload(InventoryItemModel.product_attributes))
            .filter(InventoryItemModel.id == item_id)
        )
        return result.scalars().first()

    async def get_by_code(self, item_code: str) -> Optional[InventoryItemModel]:
        result = await self.session.execute(
            select(InventoryItemModel)
            .options(selectinload(InventoryItemModel.product_attributes))
            .filter(InventoryItemModel.item_code == item_code)
        )
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[InventoryItemModel]:
        result = await self.session.execute(
            select(InventoryItemModel)
            .options(selectinload(InventoryItemModel.product_attributes))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_product_attributes_by_ids(self, attribute_ids: List[UUID]) -> List[ProductAttributeModel]:
        if not attribute_ids:
            return []
        result = await self.session.execute(
            select(ProductAttributeModel).filter(ProductAttributeModel.id.in_(attribute_ids))
        )
        return list(result.scalars().all())

    async def create(self, item: InventoryItemModel) -> InventoryItemModel:
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def update(self, item: InventoryItemModel) -> InventoryItemModel:
        await self.session.commit()
        await self.session.refresh(item)
        return item
