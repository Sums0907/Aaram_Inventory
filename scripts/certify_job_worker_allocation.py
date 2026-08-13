import asyncio
import os
import sys
import uuid
from decimal import Decimal
from datetime import date

# Ensure the app context is available
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["DATABASE_ENV"] = "test"

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.foundation.database.session import Base
from src.domains.masters.models.supplier import Supplier
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.inventory.models.job_work import JobWorkIssueModel, JobWorkerInventoryModel, JobWorkAllocationModel
from src.domains.inventory.schemas.job_work import JobWorkIssueCreate, JobWorkReturnCreate
from src.domains.inventory.services.job_work import JobWorkService
from src.domains.inventory.repositories.job_work import JobWorkRepository
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService
from src.domains.inventory.services.transformation_engine import InventoryTransformationEngine, TransformationRequest
from src.domains.inventory.schemas.enums import TransformationReason
from src.domains.masters.models.bom import BOMModel, BOMItemModel
from sqlalchemy import select, delete

async def create_test_data(session):
    # Setup Warehouse
    warehouse = WarehouseModel(
        warehouse_code="WH-TEST",
        warehouse_name="Test Warehouse",
        address_line_1="Test",
        city="Test",
        state="Test",
        pin_code="123456"
    )
    session.add(warehouse)
    
    # Setup Job Worker
    jw = Supplier(name="ABC Textiles", is_job_worker=True)
    session.add(jw)
    
    from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
    from sqlalchemy import select
    stmt = select(UnitOfMeasureModel).limit(1)
    res = await session.execute(stmt)
    uom_rm = res.scalars().first()
    if not uom_rm:
        uom_rm = UnitOfMeasureModel(unit_code="MTR-T", unit_name="Meter-T", short_name="m-t", unit_type="DECIMAL")
        session.add(uom_rm)
        await session.flush()
    
    # Setup Raw Material
    p_rm = ProductModel(product_code="PRD-RM", product_name="Cotton Fabric", item_type="RAW_MATERIAL")
    session.add(p_rm)
    await session.flush()
    sku_rm = SKUModel(product_id=p_rm.id, sku_code="SKU-RM", item_code="ITM-RM", uom_id=uom_rm.id)
    session.add(sku_rm)
    
    # Setup Finished Good
    p_fg = ProductModel(product_code="PRD-FG", product_name="Cotton Bedsheet", item_type="FINISHED_GOODS")
    session.add(p_fg)
    await session.flush()
    sku_fg = SKUModel(product_id=p_fg.id, sku_code="SKU-FG", item_code="ITM-FG")
    session.add(sku_fg)
    await session.flush()
    
    # Setup BOM: 1 FG = 2.875 RM
    bom = BOMModel(bom_number="BOM-01", bom_name="Test BOM", target_item_id=sku_fg.id, status="ACTIVE")
    session.add(bom)
    await session.flush()
    bom_item = BOMItemModel(bom_id=bom.id, component_item_id=sku_rm.id, quantity=Decimal("2.875"))
    session.add(bom_item)
    
    # Give initial stock to warehouse
    from src.domains.inventory.models.movement import InventoryMovementModel
    init_stock = InventoryMovementModel(
        movement_number="INIT-1",
        movement_type="PURCHASE_RECEIPT",
        movement_date=date.today(),
        posting_date=date.today(),
        status="POSTED",
        warehouse_id=warehouse.id,
        sku_id=sku_rm.id,
        quantity=Decimal("10000.000"),
        unit_cost=0.0,
        reference_type="INIT",
        reference_number="INIT",
        reference_id=uuid.uuid4()
    )
    session.add(init_stock)
    
    await session.commit()
    
    return warehouse.id, jw.id, sku_rm.id, sku_fg.id

async def run_tests():
    engine = create_async_engine("sqlite+aiosqlite:///./test_cert_allocation.db")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        try:
            # Clean up
            await session.execute(delete(JobWorkAllocationModel))
            await session.execute(delete(JobWorkIssueModel))
            await session.execute(delete(JobWorkerInventoryModel))
            
            from src.domains.inventory.models.movement import InventoryMovementModel
            await session.execute(delete(InventoryMovementModel))
            await session.execute(delete(BOMItemModel))
            await session.execute(delete(BOMModel))
            await session.execute(delete(SKUModel))
            await session.execute(delete(ProductModel))
            from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
            await session.execute(delete(UnitOfMeasureModel))
            await session.execute(delete(Supplier))
            await session.execute(delete(WarehouseModel))
            
            await session.commit()
            
            wh_id, jw_id, rm_id, fg_id = await create_test_data(session)
            
            repo = JobWorkRepository(session)
            mov_repo = InventoryMovementRepository(session)
            class MockBalanceCalculator:
                async def recalculate_balance(self, *args, **kwargs):
                    pass
            bal_calc = MockBalanceCalculator()
            mov_svc = InventoryMovementService(mov_repo, bal_calc)
            jw_svc = JobWorkService(repo, mov_svc)
            tx_engine = InventoryTransformationEngine(mov_svc)
            
            admin_id = uuid.uuid4()
            
            print("--- Running Certification Tests ---")
            
            # TEST A: Multiple Issues
            print("Running Test A - Multiple Issues...")
            await jw_svc.issue_material(JobWorkIssueCreate(job_worker_id=jw_id, item_id=rm_id, quantity=280.0, warehouse_id=wh_id), admin_id)
            await jw_svc.issue_material(JobWorkIssueCreate(job_worker_id=jw_id, item_id=rm_id, quantity=250.0, warehouse_id=wh_id), admin_id)
            await jw_svc.issue_material(JobWorkIssueCreate(job_worker_id=jw_id, item_id=rm_id, quantity=300.0, warehouse_id=wh_id), admin_id)
            
            stock = await jw_svc.get_pending_stock(jw_id)
            assert len(stock) == 1
            assert stock[0].pending_quantity == Decimal("830.000"), f"Expected 830, got {stock[0].pending_quantity}"
            
            stmt = select(JobWorkIssueModel).where(JobWorkIssueModel.job_worker_id == jw_id).order_by(JobWorkIssueModel.created_on.asc())
            res = await session.execute(stmt)
            issues = res.scalars().all()
            assert len(issues) == 3
            
            # TEST B & G: FIFO Consumption & Decimal Precision (100 * 2.875 = 287.50)
            print("Running Test B & G - FIFO Consumption and Decimal Precision...")
            req = TransformationRequest(target_sku_id=fg_id, target_quantity=100, job_worker_id=jw_id, reference_document="REC-001", warehouse_id=wh_id)
            await tx_engine.execute_transformation(req, admin_id, session)
            await session.commit()
            
            # Verify Job Worker Stock summary
            await session.refresh(stock[0])
            assert stock[0].consumed_quantity == Decimal("287.500")
            assert stock[0].pending_quantity == Decimal("542.500") # 830 - 287.5 = 542.5
            
            # Verify allocations
            await session.refresh(issues[0])
            await session.refresh(issues[1])
            await session.refresh(issues[2])
            
            assert issues[0].consumed_quantity == Decimal("280.000")
            assert issues[0].pending_quantity == Decimal("0.000")
            
            assert issues[1].consumed_quantity == Decimal("7.500")
            assert issues[1].pending_quantity == Decimal("242.500") # Test C: Partial Issue Consumption
            
            assert issues[2].consumed_quantity == Decimal("0.000")
            assert issues[2].pending_quantity == Decimal("300.000")
            
            # Verify allocations table
            stmt = select(JobWorkAllocationModel)
            res = await session.execute(stmt)
            allocs = res.scalars().all()
            assert len(allocs) == 2
            
            # TEST E: Return
            print("Running Test E - Return...")
            await jw_svc.return_material(JobWorkReturnCreate(job_worker_id=jw_id, item_id=rm_id, quantity=42.5, warehouse_id=wh_id), admin_id)
            
            await session.refresh(stock[0])
            assert stock[0].returned_quantity == Decimal("42.500")
            assert stock[0].pending_quantity == Decimal("500.000")
            
            await session.refresh(issues[1])
            assert issues[1].returned_quantity == Decimal("42.500")
            assert issues[1].pending_quantity == Decimal("200.000")
            
            # TEST F: Over-Return
            print("Running Test F - Over-Return...")
            try:
                await jw_svc.return_material(JobWorkReturnCreate(job_worker_id=jw_id, item_id=rm_id, quantity=1000.0, warehouse_id=wh_id), admin_id)
                assert False, "Should have failed over-return"
            except Exception:
                await session.rollback() # Full rollback
                
            # Re-fetch after rollback
            stock = await jw_svc.get_pending_stock(jw_id)
            assert stock[0].pending_quantity == Decimal("500.000")
            
            # TEST H: Historical Allocation
            print("Running Test H - Historical Allocation...")
            await jw_svc.issue_material(JobWorkIssueCreate(job_worker_id=jw_id, item_id=rm_id, quantity=100.0, warehouse_id=wh_id), admin_id)
            
            # Old allocations should not change
            stmt = select(JobWorkAllocationModel).where(JobWorkAllocationModel.allocation_type == "CONSUMPTION")
            res = await session.execute(stmt)
            cons_allocs = res.scalars().all()
            assert sum(a.quantity for a in cons_allocs) == Decimal("287.500")
            
            print("All Certification Tests Passed Successfully!")
            
        except AssertionError as ae:
            print(f"Test Failed: {ae}")
        except Exception as e:
            print(f"Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
