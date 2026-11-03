import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.domains.masters.models.warehouse import WarehouseModel
import uuid

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///./test_manual.db")
    TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)
    
    warehouse_id = uuid.UUID("96c6b20c-d119-4f97-b635-c8e5ef87fd52")
    
    async with TestingSessionLocal() as session:
        # Check if exists
        w = await session.get(WarehouseModel, warehouse_id)
        if not w:
            new_w = WarehouseModel(
                id=warehouse_id,
                warehouse_code="MAIN",
                warehouse_name="Main Warehouse",
                description="Default Main Warehouse",
                address_line_1="123 Main St",
                city="Delhi",
                state="Delhi",
                country="India",
                pin_code="110001"
            )
            session.add(new_w)
            await session.commit()
            print(f"Created warehouse: {warehouse_id}")
        else:
            print("Warehouse already exists.")

asyncio.run(main())
