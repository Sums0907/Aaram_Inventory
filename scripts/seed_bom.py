import asyncio
from uuid import UUID
from datetime import datetime
from src.app.container import DomainsContainer
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.bom import BOMModel, BOMItemModel
from src.foundation.enums.status import GenericStatus

async def main():
    import os
    os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test_manual.db'
    os.environ['DATABASE_URL_SYNC'] = 'sqlite:///./test_manual.db'
    
    container = DomainsContainer()
    from src.foundation.configuration import get_settings
    container.core.config.from_dict(get_settings().model_dump())
    container.init_resources()
    
    db = container.core.db()
    
    async with db._session_factory() as session:
        # Find Blue Bay Bedsheet SKU
        from sqlalchemy import select
        stmt = select(SKUModel).where(SKUModel.sku_code == 'FG-BBB-001')
        res = await session.execute(stmt)
        fg_sku = res.scalars().first()
        
        if not fg_sku:
            print("Finished goods not found!")
            return
            
        stmt = select(SKUModel).where(SKUModel.sku_code == 'RM-DF-001')
        res = await session.execute(stmt)
        rm_sku = res.scalars().first()
        
        if not rm_sku:
            print("Raw material not found!")
            return
            
        print(f"Creating BOM v2 for {fg_sku.id} using {rm_sku.id}")
        
        bom = BOMModel(
            bom_number="BOM-BBB-V2",
            target_item_id=fg_sku.id,
            target_quantity=1,
            version=2,
            status=GenericStatus.ACTIVE,
            effective_from=datetime(2024, 6, 1),
            items=[
                BOMItemModel(
                    component_item_id=rm_sku.id,
                    quantity=3.0,
                    wastage_percentage=0.10,
                    tolerance_percentage=0.05
                )
            ]
        )
        
        session.add(bom)
        await session.commit()
        print("BOM v2 created!")

if __name__ == "__main__":
    asyncio.run(main())
