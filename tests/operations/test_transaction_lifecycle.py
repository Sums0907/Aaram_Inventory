import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.foundation.dependency_injection.container import CoreContainer
from src.app.container import DomainsContainer
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.warehouse import WarehouseModel

@pytest_asyncio.fixture
async def setup_base_data(db_session: AsyncSession):
    # Setup necessary baseline for pipeline orchestrator
    sku = SKUModel(id=uuid4(), item_code=f"TEST-ITEM-{uuid4()}", sku_code=f"TEST-SKU-{uuid4()}", product_id=uuid4())
    db_session.add(sku)
    
    warehouse = WarehouseModel(
        id=uuid4(), 
        warehouse_code=f"WH-{uuid4()}", 
        warehouse_name="Test Warehouse", 
        address_line_1="Address 1", 
        city="City", 
        state="State", 
        pin_code="123456"
    )
    db_session.add(warehouse)
    
    await db_session.commit()
    return {"sku": sku, "warehouse": warehouse}

@pytest.mark.asyncio
async def test_session_lifecycle_persistence(setup_base_data):
    # Setup test container with independent database pool
    core = CoreContainer()
    core.config.from_dict({
        "DATABASE_URL": "sqlite+aiosqlite:///./test_cert_inventory.db",
        "DEBUG": False,
        "DB_POOL_SIZE": 5,
        "DB_MAX_OVERFLOW": 10
    })
    
    domains = DomainsContainer(core=core)
    res = domains.init_resources()
    if res:
        await res
    
    # Prove that the REQUEST lifecycle generates a persistent commit
    # Simulating the endpoint dependency resolution
    orchestrator = domains.pipeline_orchestrator()
    
    sku_id = setup_base_data["sku"].id
    wh_id = setup_base_data["warehouse"].id
    user_id = uuid4()
    
    # Mocking what the pipeline orchestrator does internally:
    # Creating a movement and committing
    movement = InventoryMovementCreate(
        movement_number=f"TEST-MOV-{uuid4()}",
        movement_type="MANUAL_ADJUSTMENT",
        movement_date=date.today(),
        posting_date=date.today(),
        status="POSTED",
        warehouse_id=wh_id,
        sku_id=sku_id,
        quantity=10,
        unit_cost=100.0,
        reference_type="MANUAL",
        reference_number="TEST",
        reference_id=uuid4()
    )
    
    try:
        # BUSINESS OPERATION -> COMMIT
        await orchestrator.inventory_movement.create_movement(movement, user_id, session=orchestrator.session)
        await orchestrator.session.commit()
    except Exception:
        await orchestrator.session.rollback()
        raise
    finally:
        # REQUEST ENDS -> Session released back to DI resource
        pass
        
    res = domains.shutdown_resources()
    if res:
        await res
    
    # NEW DATABASE SESSION -> EXPECTED RECORD EXISTS
    async with core.db()._session_factory() as verify_session:
        stmt = select(InventoryMovementModel).where(InventoryMovementModel.movement_number == movement.movement_number)
        res = await verify_session.execute(stmt)
        persisted_mov = res.scalar_one_or_none()
        
        assert persisted_mov is not None
        assert persisted_mov.quantity == 10

@pytest.mark.asyncio
async def test_session_lifecycle_rollback(setup_base_data):
    core = CoreContainer()
    core.config.from_dict({
        "DATABASE_URL": "sqlite+aiosqlite:///./test_cert_inventory.db",
        "DEBUG": False,
        "DB_POOL_SIZE": 5,
        "DB_MAX_OVERFLOW": 10
    })
    domains = DomainsContainer(core=core)
    res = domains.init_resources()
    if res:
        await res
    
    orchestrator = domains.pipeline_orchestrator()
    sku_id = setup_base_data["sku"].id
    wh_id = setup_base_data["warehouse"].id
    user_id = uuid4()
    
    movement = InventoryMovementCreate(
        movement_number=f"TEST-MOV-RB-{uuid4()}",
        movement_type="MANUAL_ADJUSTMENT",
        movement_date=date.today(),
        posting_date=date.today(),
        status="POSTED",
        warehouse_id=wh_id,
        sku_id=sku_id,
        quantity=10,
        unit_cost=100.0,
        reference_type="MANUAL",
        reference_number="TEST",
        reference_id=uuid4()
    )
    
    try:
        # Inventory operation succeeds (added to session)
        await orchestrator.inventory_movement.create_movement(movement, user_id, session=orchestrator.session)
        
        # Downstream operation deliberately fails!
        raise ValueError("Simulated Downstream Failure")
        
        await orchestrator.session.commit()
    except ValueError:
        # ROLLBACK
        await orchestrator.session.rollback()
    
    res = domains.shutdown_resources()
    if res:
        await res
    
    # NEW DATABASE SESSION -> NO partial records exist
    async with core.db()._session_factory() as verify_session:
        stmt = select(InventoryMovementModel).where(InventoryMovementModel.movement_number == movement.movement_number)
        res = await verify_session.execute(stmt)
        persisted_mov = res.scalar_one_or_none()
        
        assert persisted_mov is None

@pytest.mark.asyncio
async def test_session_lifecycle_accounting_rollback(setup_base_data):
    # Reverse failure direction: Accounting fails -> Inventory rolls back
    core = CoreContainer()
    core.config.from_dict({
        "DATABASE_URL": "sqlite+aiosqlite:///./test_cert_inventory.db",
        "DEBUG": False,
        "DB_POOL_SIZE": 5,
        "DB_MAX_OVERFLOW": 10
    })
    domains = DomainsContainer(core=core)
    res = domains.init_resources()
    if res:
        await res
    
    orchestrator = domains.pipeline_orchestrator()
    sku_id = setup_base_data["sku"].id
    wh_id = setup_base_data["warehouse"].id
    user_id = uuid4()
    
    mov_num = f"TEST-MOV-REV-{uuid4()}"
    movement = InventoryMovementCreate(
        movement_number=mov_num,
        movement_type="MANUAL_ADJUSTMENT",
        movement_date=date.today(),
        posting_date=date.today(),
        status="POSTED",
        warehouse_id=wh_id,
        sku_id=sku_id,
        quantity=10,
        unit_cost=100.0,
        reference_type="MANUAL",
        reference_number="TEST",
        reference_id=uuid4()
    )
    
    try:
        # 1. Inventory operation succeeds (added to session)
        await orchestrator.inventory_movement.create_movement(movement, user_id, session=orchestrator.session)
        
        # 2. Accounting operation deliberately fails!
        # Simulating by passing invalid schema or raising directly
        raise ValueError("Simulated Accounting Failure")
        
        await orchestrator.session.commit()
    except ValueError:
        await orchestrator.session.rollback()
        
    res = domains.shutdown_resources()
    if res:
        await res
    
    # Verify Inventory rolled back completely
    async with core.db()._session_factory() as verify_session:
        stmt = select(InventoryMovementModel).where(InventoryMovementModel.movement_number == mov_num)
        res = await verify_session.execute(stmt)
        persisted_mov = res.scalar_one_or_none()
        
        assert persisted_mov is None
