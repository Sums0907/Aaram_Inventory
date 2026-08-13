from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.models.bom import BOMModel, BOMItemModel
from src.domains.masters.schemas.bom import BOMCreate

class BOMRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_bom(self, schema: BOMCreate, created_by: UUID) -> BOMModel:
        db_obj = BOMModel(
            bom_number=schema.bom_number,
            target_item_id=schema.target_item_id,
            target_quantity=schema.target_quantity,
            status=schema.status,
            created_by=created_by,
            updated_by=created_by
        )
        self.session.add(db_obj)
        await self.session.commit()
        from src.domains.masters.models.sku import SKUModel
        from sqlalchemy import select
        
        component_ids = [item.component_item_id for item in schema.items]
        stmt = select(SKUModel.id, SKUModel.uom_id).where(SKUModel.id.in_(component_ids))
        res = await self.session.execute(stmt)
        sku_uom_map = {row.id: row.uom_id for row in res.all()}
        
        for item in schema.items:
            uom_id = sku_uom_map.get(item.component_item_id)
            if not uom_id and str(item.component_item_id) in str(sku_uom_map):
                # We allow components without UOM (like existing Finished Goods)
                pass
                
            bom_item = BOMItemModel(
                bom_id=db_obj.id,
                component_item_id=item.component_item_id,
                quantity=item.quantity,
                uom_id=uom_id,
                unit_of_measure="Inherited", # SQLite constraint filler
                created_by=created_by,
                updated_by=created_by
            )
            self.session.add(bom_item)
            
        await self.session.commit()
        return await self.get_bom(db_obj.id)

    async def get_bom(self, bom_id: UUID) -> Optional[BOMModel]:
        stmt = select(BOMModel).options(selectinload(BOMModel.items)).where(BOMModel.id == bom_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_all(self) -> List[BOMModel]:
        stmt = select(BOMModel).options(selectinload(BOMModel.items))
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_by_target_item_id(self, target_item_id: UUID) -> List[BOMModel]:
        stmt = select(BOMModel).where(BOMModel.target_item_id == target_item_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()
        
    async def get_boms_for_items(self, item_ids: List[UUID]) -> List[BOMModel]:
        if not item_ids:
            return []
        stmt = select(BOMModel).where(BOMModel.target_item_id.in_(item_ids))
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_boms_using_component(self, component_item_id: UUID) -> int:
        from sqlalchemy import func
        from src.foundation.enums.status import GenericStatus
        stmt = (
            select(func.count(func.distinct(BOMModel.id)))
            .join(BOMItemModel, BOMModel.id == BOMItemModel.bom_id)
            .where(
                BOMItemModel.component_item_id == component_item_id,
                BOMModel.status.in_([GenericStatus.ACTIVE, GenericStatus.DRAFT])
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar() or 0

    async def archive_bom(self, bom_id: UUID) -> bool:
        stmt = select(BOMModel).where(BOMModel.id == bom_id)
        res = await self.session.execute(stmt)
        bom = res.scalars().first()
        if not bom:
            return False
        bom.status = "ARCHIVED"
        await self.session.commit()
        return True

    async def restore_bom(self, bom_id: UUID) -> bool:
        stmt = select(BOMModel).where(BOMModel.id == bom_id)
        res = await self.session.execute(stmt)
        bom = res.scalars().first()
        if not bom:
            return False
        bom.status = "ACTIVE"
        await self.session.commit()
        return True
