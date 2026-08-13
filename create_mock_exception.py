import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.domains.inventory.models.exception import InventoryExceptionModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.warehouse import WarehouseModel
from sqlalchemy import select

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///./test_manual.db")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        sku = (await session.execute(select(SKUModel).limit(1))).scalars().first()
        warehouse = (await session.execute(select(WarehouseModel).limit(1))).scalars().first()
        
        if not sku or not warehouse:
            print("No SKU or Warehouse found")
            return
            
        # Check if exception already exists
        existing = (await session.execute(select(InventoryExceptionModel).limit(1))).scalars().first()
        if existing:
            print("Exception already exists")
            return
            
        exc = InventoryExceptionModel(
            exception_number=f"EXC-{uuid.uuid4().hex[:6].upper()}",
            warehouse_id=warehouse.id,
            sku_id=sku.id,
            exception_date=datetime.now(timezone.utc),
            source_system="SHOPDECK_SYNC",
            expected_quantity=50,
            actual_quantity=45,
            difference=-5,
            status="OPEN"
        )
        session.add(exc)
        await session.commit()
        print("Mock exception created")

if __name__ == "__main__":
    asyncio.run(main())
