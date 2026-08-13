import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from src.domains.inventory.models.balance import InventoryBalanceModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.warehouse import WarehouseModel

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///./test_manual.db")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        stmt = select(
            WarehouseModel.warehouse_name,
            WarehouseModel.id.label("warehouse_id"),
            SKUModel.id.label("sku_id"),
            SKUModel.sku_code,
            ProductModel.product_name.label("sku_name"),
            InventoryBalanceModel.quantity_on_hand,
            InventoryBalanceModel.confidence_score
        ).select_from(SKUModel)\
         .join(ProductModel, ProductModel.id == SKUModel.product_id)\
         .join(WarehouseModel, WarehouseModel.is_active == True)\
         .outerjoin(
             InventoryBalanceModel,
             (InventoryBalanceModel.sku_id == SKUModel.id) & 
             (InventoryBalanceModel.warehouse_id == WarehouseModel.id)
         )
         
        result = await session.execute(stmt)
        records = result.all()
        for r in records:
            print(r)

if __name__ == "__main__":
    asyncio.run(main())
