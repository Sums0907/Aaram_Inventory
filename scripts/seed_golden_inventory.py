import asyncio
import uuid
import random
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from src.foundation.database.session import Base
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService
from src.domains.inventory.services.confidence_engine import ConfidenceEngine
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.repositories.exception import InventoryExceptionRepository

import os
os.environ["DATABASE_ENV"] = "test"
DATABASE_URL = "sqlite+aiosqlite:///./test_seed.db"

async def main():
    print("Seeding Golden Inventory Data...")
    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        # Get default warehouse or create one
        result = await session.execute(select(WarehouseModel))
        warehouse = result.scalars().first()
        if not warehouse:
            warehouse = WarehouseModel(
                id=uuid.uuid4(),
                warehouse_code="WH-MAIN",
                warehouse_name="Main Warehouse",
                address_line_1="123 Industrial Area",
                city="Mumbai",
                state="MH",
                pin_code="400001"
            )
            session.add(warehouse)
            await session.commit()
            
        result = await session.execute(select(SKUModel))
        skus = result.scalars().all()
        
        if not skus:
            print("No SKUs found. Run ingest_product_master.py first.")
            return
            
        # Select 20 random SKUs to have inventory activity
        active_skus = random.sample(skus, min(20, len(skus)))
        
        system_user = uuid.uuid4()
        
        movement_repo = InventoryMovementRepository(session)
        balance_repo = InventoryBalanceRepository(session)
        exception_repo = InventoryExceptionRepository(session)
        confidence_engine = ConfidenceEngine(exception_repo, movement_repo)
        balance_calc = BalanceCalculatorService(balance_repo, movement_repo, exception_repo, confidence_engine)
        
        for sku in active_skus:
            # 1. Initial Stock (10 to 500 units)
            initial_qty = random.randint(10, 500)
            mov1 = InventoryMovementModel(
                id=uuid.uuid4(),
                movement_number=f"INIT-{sku.sku_code}-{random.randint(1000, 9999)}",
                movement_type="INITIAL_STOCK",
                movement_date=date.today() - timedelta(days=random.randint(10, 30)),
                posting_date=date.today(),
                status="POSTED",
                warehouse_id=warehouse.id,
                sku_id=sku.id,
                quantity=initial_qty,
                unit_cost=100.0,
                reference_type="STOCK_TAKE",
                reference_number="STK-001",
                reference_id=uuid.uuid4(),
                created_by=system_user,
                updated_by=system_user
            )
            session.add(mov1)
            
            # 2. Sales (reduce stock)
            sales_qty = random.randint(1, initial_qty + 50) # chance of going negative
            mov2 = InventoryMovementModel(
                id=uuid.uuid4(),
                movement_number=f"SALES-{sku.sku_code}-{random.randint(1000, 9999)}",
                movement_type="SALES_FULFILLMENT",
                movement_date=date.today() - timedelta(days=random.randint(1, 9)),
                posting_date=date.today(),
                status="POSTED",
                warehouse_id=warehouse.id,
                sku_id=sku.id,
                quantity=-sales_qty,
                unit_cost=100.0,
                reference_type="TAX_INVOICE",
                reference_number="INV-001",
                reference_id=uuid.uuid4(),
                created_by=system_user,
                updated_by=system_user
            )
            session.add(mov2)
            
            # Commit movements
            await session.commit()
            
            # 3. Recalculate Balance
            try:
                await balance_calc.recalculate_balance(warehouse.id, sku.id)
            except Exception as e:
                print(f"Exception for {sku.sku_code}: {e}")
                
            # 4. Recalculate Confidence
            await confidence_engine.calculate_confidence(sku.id)
            
        print(f"Successfully seeded inventory movements and balances for {len(active_skus)} SKUs.")

if __name__ == "__main__":
    asyncio.run(main())
