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
            selectinload(SKUModel.uom),
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
        
    async def get_bom_health_kpi(self) -> dict:
        from src.domains.masters.models.product import ProductModel
        from src.domains.masters.models.bom import BOMModel
        from src.foundation.enums import ItemType
        from sqlalchemy import func
        
        # Total finished goods SKUs
        stmt_total = select(func.count(SKUModel.id)).join(ProductModel).where(ProductModel.item_type == ItemType.FINISHED_GOODS)
        total_fg = await self.session.execute(stmt_total)
        total_fg_count = total_fg.scalar() or 0
        
        # Finished goods SKUs with BOMs
        stmt_boms = select(func.count(func.distinct(SKUModel.id))).join(ProductModel).join(BOMModel, SKUModel.id == BOMModel.target_item_id).where(ProductModel.item_type == ItemType.FINISHED_GOODS)
        boms_fg = await self.session.execute(stmt_boms)
        boms_fg_count = boms_fg.scalar() or 0
        
        return {
            "total_finished_goods": total_fg_count,
            "configured_boms": boms_fg_count,
            "missing_boms": total_fg_count - boms_fg_count
        }

    async def create(self, sku: SKUModel) -> SKUModel:
        self.session.add(sku)
        await self.session.commit()
        await self.session.refresh(sku)
        return sku

    async def update(self, sku: SKUModel) -> SKUModel:
        await self.session.commit()
        await self.session.refresh(sku)
        return sku

    async def delete(self, sku: SKUModel) -> None:
        await self.session.delete(sku)
        await self.session.commit()
