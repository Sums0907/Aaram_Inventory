import asyncio
from uuid_extensions import uuid7
from src.app.container import DomainsContainer
from src.domains.masters.models.bom import BOMModel, BOMItemModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.foundation.enums.item_type import ItemType
from src.foundation.enums.status import GenericStatus
from src.domains.data_ingestion.services.exporters.bom_exporter import BOMExporter

async def test_bom():
    container = DomainsContainer()
    container.core.config.from_dict({"DATABASE_URL": "sqlite+aiosqlite:///test_create_cat.db", "DATABASE_ENV": "development"})
    
    db = container.core.db()
    async with db._session_factory() as session:
        # Create UOM
        uom = UnitOfMeasureModel(unit_code="KG", unit_name="Kilogram")
        session.add(uom)
        
        # Create Category
        cat = CategoryModel(category_code="C1", category_name="Cat", item_type=ItemType.FINISHED_GOODS)
        session.add(cat)
        
        # Create Product
        prod = ProductModel(product_code="P1", product_name="Prod", category_id=cat.id)
        session.add(prod)
        
        # Create SKU
        sku = SKUModel(sku_code="SKU1", item_code="SKU1", product_id=prod.id)
        session.add(sku)
        
        # Create BOM
        bom = BOMModel(
            bom_number="BOM1",
            target_item_id=sku.id,
            target_quantity=1
        )
        session.add(bom)
        
        # Create BOM Item
        bom_item = BOMItemModel(
            bom_id=bom.id,
            component_item_id=sku.id,
            quantity=2,
            uom_id=uom.id
        )
        session.add(bom_item)
        
        await session.commit()
        
    async with db._session_factory() as session:
        exporter = BOMExporter(session)
        try:
            data = await exporter.export_data()
            print("Successfully exported", len(data), "BOM rows.")
            print(data)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bom())
