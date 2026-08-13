import asyncio
from src.foundation.database.session import Database
from src.domains.inventory.schemas.goods_receipt import GoodsReceiptCreate, GoodsReceiptItemCreate
from src.domains.inventory.services.goods_receipt import GoodsReceiptService
from src.domains.inventory.repositories.goods_receipt import GoodsReceiptRepository
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService
from src.domains.inventory.services.transformation_engine import InventoryTransformationEngine
import uuid
from datetime import date

async def test():
    db = Database("sqlite+aiosqlite:///test_manual.db", False, 0, 0)
    
    # 1. Fetch valid SKU with BOM
    async with db._session_factory() as session:
        from sqlalchemy import text
        res = await session.execute(text("SELECT target_item_id FROM masters_boms LIMIT 1"))
        sku_id = res.scalar()
        if not sku_id:
            print("NO BOM FOUND")
            return
            
        print("Using SKU", sku_id)
        
        # 2. Get a warehouse
        res = await session.execute(text("SELECT id FROM warehouses LIMIT 1"))
        warehouse_id = res.scalar()
        
        # 3. Get a job worker (supplier)
        res = await session.execute(text("SELECT id FROM masters_suppliers WHERE supplier_type = 'JOB_WORKER' LIMIT 1"))
        supplier_id = res.scalar()
        if not supplier_id:
            res = await session.execute(text("SELECT id FROM masters_suppliers LIMIT 1"))
            supplier_id = res.scalar()

    # 4. Try creating GRN
    async with db._session_factory() as session:
        grn_repo = GoodsReceiptRepository(session)
        mov_repo = InventoryMovementRepository(session)
        bal_calc = BalanceCalculatorService(session)
        mov_service = InventoryMovementService(mov_repo, bal_calc)
        transform_engine = InventoryTransformationEngine(mov_service)
        service = GoodsReceiptService(grn_repo, mov_service, transform_engine)

        schema = GoodsReceiptCreate(
            grn_number=f"TEST-GRN-{uuid.uuid4().hex[:4]}",
            supplier_id=supplier_id,
            warehouse_id=warehouse_id,
            receipt_date=date.today(),
            receipt_type="JOB_WORK_RECEIPT",
            items=[
                GoodsReceiptItemCreate(
                    sku_id=sku_id,
                    quantity=1,
                )
            ]
        )
        try:
            print("Creating GRN...")
            res = await service.create(schema, uuid.uuid4())
            print("SUCCESS!", res.grn_number)
        except Exception as e:
            print("ERROR", type(e))
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
