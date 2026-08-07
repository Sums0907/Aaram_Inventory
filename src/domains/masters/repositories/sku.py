from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import cast, JSON
from sqlalchemy.orm import selectinload
from src.domains.masters.models.sku import SKUModel

class SKURepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _base_query(self):
        return select(SKUModel).options(
            selectinload(SKUModel.product),
            selectinload(SKUModel.pricing),
            selectinload(SKUModel.images)
        )

    async def get_by_id(self, sku_id: UUID) -> Optional[SKUModel]:
        result = await self.session.execute(self._base_query().filter(SKUModel.id == sku_id))
        return result.scalars().first()

    async def get_by_code(self, sku_code: str) -> Optional[SKUModel]:
        result = await self.session.execute(self._base_query().filter(SKUModel.sku_code == sku_code))
        return result.scalars().first()
        
    async def get_by_barcode(self, barcode: str) -> Optional[SKUModel]:
        result = await self.session.execute(self._base_query().filter(SKUModel.barcode == barcode))
        return result.scalars().first()
        
    async def get_by_product_and_attributes(self, product_id: UUID, attributes: Dict[str, Any]) -> Optional[SKUModel]:
        # Exact JSONB match
        result = await self.session.execute(
            self._base_query().filter(
                SKUModel.product_id == product_id,
                SKUModel.attribute_values == attributes
            )
        )
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[SKUModel]:
        result = await self.session.execute(self._base_query().offset(skip).limit(limit))
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
