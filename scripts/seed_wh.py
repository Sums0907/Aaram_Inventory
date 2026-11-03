import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from src.domains.masters.models.warehouse import WarehouseModel
from src.foundation.enums.status import GenericStatus
import uuid

async def seed_warehouse():
    engine = create_async_engine("postgresql+asyncpg://postgres:password@localhost:5433/inventory_dev")
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        wh_id = uuid.UUID('dbcfca97-fc1d-4466-815f-a843072a14be')
        result = await session.execute(select(WarehouseModel).filter_by(id=wh_id))
        wh = result.scalars().first()
        if not wh:
            wh = WarehouseModel(
                id=wh_id,
                warehouse_code="WH-MAIN",
                warehouse_name="Main Warehouse",
                address_line_1="Aaram Books HQ",
                city="Delhi",
                state="Delhi",
                country="India",
                pin_code="110001",
                status=GenericStatus.ACTIVE
            )
            session.add(wh)
            await session.commit()
            print("Warehouse seeded via ORM successfully.")
        else:
            print("Warehouse already exists.")

asyncio.run(seed_warehouse())
