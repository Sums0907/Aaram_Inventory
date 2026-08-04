from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import cast
from src.domains.masters.models.sku import SKUModel

class SKURepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, sku_id: UUID) -> Optional[SKUModel]:
        result = await self.session.execute(select(SKUModel).filter(SKUModel.id == sku_id))
        return result.scalars().first()

    async def get_by_code(self, sku_code: str) -> Optional[SKUModel]:
        result = await self.session.execute(select(SKUModel).filter(SKUModel.sku_code == sku_code))
        return result.scalars().first()
        
    async def get_by_barcode(self, barcode: str) -> Optional[SKUModel]:
        result = await self.session.execute(select(SKUModel).filter(SKUModel.barcode == barcode))
        return result.scalars().first()
        
    async def get_by_item_and_attributes(self, item_id: UUID, attributes: Dict[str, Any]) -> Optional[SKUModel]:
        # Exact JSONB match
        result = await self.session.execute(
            select(SKUModel).filter(
                SKUModel.inventory_item_id == item_id,
                cast(SKUModel.attribute_values, JSONB) == cast(attributes, JSONB)
            )
        )
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[SKUModel]:
        result = await self.session.execute(select(SKUModel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, sku: SKUModel) -> SKUModel:
        self.session.add(sku)
        await self.session.commit()
        await self.session.refresh(sku)
        return sku

    async def update(self, sku: SKUModel) -> SKUModel:
        await self.session.commit()
        await self.session.refresh(sku)
        return sku
