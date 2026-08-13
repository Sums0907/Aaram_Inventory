import pytest
import pytest_asyncio
from datetime import date, datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.models.lifecycle import CustomerReturnPolicyModel, OrderStateTransitionModel
from src.domains.operations.schemas.lifecycle import LifecycleState, TransitionType
from src.domains.operations.services.report_window import ShopDeckReportWindowService, DateProvider
from src.domains.operations.services.lifecycle_engine import LifecycleEngine, UnknownShopDeckStatusException
from src.domains.operations.services.reconciliation_orchestrator import ReconciliationOrchestratorService
from src.domains.inventory.models.movement import InventoryMovementModel

class MockDateProvider(DateProvider):
    def __init__(self, mocked_today: date):
        self.mocked_today = mocked_today
    def today(self) -> date:
        return self.mocked_today

@pytest_asyncio.fixture
async def setup_dependencies(db_session: AsyncSession):
    # Setup initial return policy (7 days)
    policy = CustomerReturnPolicyModel(
        id=uuid4(),
        effective_from=date(2026, 8, 1),
        return_window_days=7,
        is_active=True
    )
    db_session.add(policy)
    
    # Also we need a warehouse for the movement service
    from src.domains.masters.models.warehouse import WarehouseModel
    import os
    warehouse = WarehouseModel(
        id=uuid4(), 
        warehouse_code="WH-01", 
        warehouse_name="Main Warehouse", 
        address_line_1="Address 1", 
        city="City", 
        state="State", 
        pin_code="123456"
    )
    db_session.add(warehouse)
    await db_session.commit()
    os.environ["SHOPDECK_SALES_WAREHOUSE_CODE"] = "WH-01"
    
    date_provider = MockDateProvider(date(2026, 8, 19))
    
    from src.app.main import app
    orchestrator = app.domains_container.operations.reconciliation_orchestrator(session=db_session)
    orchestrator.window_service.session = db_session
    orchestrator.window_service.date_provider = date_provider
    orchestrator.lifecycle_engine.session = db_session
    orchestrator.movement_service.repository.session = db_session
    orchestrator.movement_service.balance_calculator.balance_repository.session = db_session
    orchestrator.movement_service.balance_calculator.movement_repository.session = db_session
    orchestrator.movement_service.balance_calculator.exception_repository.session = db_session
    
    return {
        "db_session": db_session,
        "window_service": orchestrator.window_service,
        "lifecycle_engine": orchestrator.lifecycle_engine,
        "orchestrator": orchestrator,
        "date_provider": date_provider
    }

async def get_inventory_movements_count(db_session: AsyncSession) -> int:
    stmt = select(func.count(InventoryMovementModel.id))
    res = await db_session.execute(stmt)
    return res.scalar() or 0

@pytest.mark.asyncio
async def test_a_to_d_new_orders(setup_dependencies):
    orchestrator = setup_dependencies["orchestrator"]
    db_session = setup_dependencies["db_session"]
    
    obs_date = date(2026, 8, 18)
    obs_datetime = datetime(2026, 8, 18, 12, 0, 0)
    
    # We pass normalized records for A, B, C, D
    records = [
        {"external_order_id": "NEW-A", "order_date": "2026-08-18", "status": "PRINT", "items": [], "observed_at": obs_datetime.isoformat()},
        {"external_order_id": "NEW-B", "order_date": "2026-08-18", "status": "HANDOVER", "items": [], "observed_at": obs_datetime.isoformat()},
        {"external_order_id": "NEW-C", "order_date": "2026-08-18", "status": "DELIVERED", "items": [], "observed_at": obs_datetime.isoformat()},
        {"external_order_id": "NEW-D", "order_date": "2026-08-18", "status": "RETURNED", "items": [], "observed_at": obs_datetime.isoformat()},
    ]
    
    # Since there are no active orders, window_service returns None for required dates, so any coverage is valid.
    summary = await orchestrator.reconcile_report(records, date(2026, 8, 18), date(2026, 8, 19))
    
    assert summary.new_shopdeck_orders == 4
    assert summary.inventory_movements_created == 0
    
    # Assert A - PRINT
    stmt = select(SalesOrderModel).where(SalesOrderModel.external_order_id == "NEW-A")
    order_a = (await db_session.execute(stmt)).scalars().first()
    assert order_a.lifecycle_state == LifecycleState.ACTIVE.value
    stmt_hist = select(OrderStateTransitionModel).where(OrderStateTransitionModel.order_id == order_a.id)
    hist_a = (await db_session.execute(stmt_hist)).scalars().first()
    assert hist_a.transition_type == TransitionType.INITIAL_OBSERVATION.value
    
    # Assert B - HANDOVER
    stmt = select(SalesOrderModel).where(SalesOrderModel.external_order_id == "NEW-B")
    order_b = (await db_session.execute(stmt)).scalars().first()
    assert order_b.lifecycle_state == LifecycleState.ACTIVE.value
    
    # Assert C - DELIVERED
    stmt = select(SalesOrderModel).where(SalesOrderModel.external_order_id == "NEW-C")
    order_c = (await db_session.execute(stmt)).scalars().first()
    assert order_c.lifecycle_state == LifecycleState.ACTIVE.value
    assert order_c.return_watch_until == obs_date + timedelta(days=7)
    
    # Assert D - RETURNED
    stmt = select(SalesOrderModel).where(SalesOrderModel.external_order_id == "NEW-D")
    order_d = (await db_session.execute(stmt)).scalars().first()
    assert order_d.lifecycle_state == LifecycleState.TERMINAL.value

def create_mock_order(db_session, ext_id, order_date, status, lifecycle_state):
    order = SalesOrderModel(
        id=uuid4(), external_order_id=ext_id, order_date=order_date, 
        status=status, channel="SHOPDECK", payment_method="COD", lifecycle_state=lifecycle_state,
        customer_name="Test User", shipping_address="Address", shipping_pincode="123", shipping_city="City", shipping_state="State"
    )
    db_session.add(order)
    return order

@pytest.mark.asyncio
async def test_e_and_f_existing_orders(setup_dependencies):
    orchestrator = setup_dependencies["orchestrator"]
    db_session = setup_dependencies["db_session"]
    
    order1 = create_mock_order(db_session, "EX-1", date(2026, 8, 15), "PRINT", "ACTIVE")
    order2 = create_mock_order(db_session, "EX-2", date(2026, 8, 15), "PACK", "ACTIVE")
    await db_session.commit()
    
    records = [
        {"external_order_id": "EX-1", "order_date": "2026-08-15", "status": "PRINT", "items": []}, # Unchanged
        {"external_order_id": "EX-2", "order_date": "2026-08-15", "status": "IN-TRANSIT", "items": []}, # Changed
    ]
    
    # Window is 15-Aug to 19-Aug
    summary = await orchestrator.reconcile_report(records, date(2026, 8, 10), date(2026, 8, 19))
    
    assert summary.unchanged_orders == 1
    assert summary.state_transitions == 1
    
    stmt = select(OrderStateTransitionModel).where(OrderStateTransitionModel.order_id == order2.id)
    hist2 = (await db_session.execute(stmt)).scalars().all()
    assert len(hist2) == 1
    assert hist2[0].transition_type == TransitionType.STATE_TRANSITION.value
    assert hist2[0].new_status == "IN-TRANSIT"

@pytest.mark.asyncio
async def test_g_same_report_uploaded_twice(setup_dependencies):
    orchestrator = setup_dependencies["orchestrator"]
    db_session = setup_dependencies["db_session"]
    
    obs_datetime = datetime(2026, 8, 18, 12, 0, 0)
    records = [
        {"external_order_id": "IDEM-1", "order_date": "2026-08-18", "status": "PRINT", "items": [], "observed_at": obs_datetime.isoformat()}
    ]
    
    summary1 = await orchestrator.reconcile_report(records, date(2026, 8, 18), date(2026, 8, 19))
    assert summary1.new_shopdeck_orders == 1
    
    summary2 = await orchestrator.reconcile_report(records, date(2026, 8, 18), date(2026, 8, 19))
    assert summary2.unchanged_orders == 1
    assert summary2.new_shopdeck_orders == 0
    
    stmt = select(SalesOrderModel).where(SalesOrderModel.external_order_id == "IDEM-1")
    orders = (await db_session.execute(stmt)).scalars().all()
    assert len(orders) == 1
    
    stmt_hist = select(OrderStateTransitionModel).where(OrderStateTransitionModel.order_id == orders[0].id)
    hists = (await db_session.execute(stmt_hist)).scalars().all()
    assert len(hists) == 1

@pytest.mark.asyncio
async def test_h_and_i_out_of_window(setup_dependencies):
    orchestrator = setup_dependencies["orchestrator"]
    db_session = setup_dependencies["db_session"]
    
    # Active order to set window to 15-Aug to 19-Aug
    order = create_mock_order(db_session, "EX-ACTIVE", date(2026, 8, 15), "PRINT", "ACTIVE")
    
    # Existing order before window
    order2 = create_mock_order(db_session, "EX-OLD", date(2026, 8, 10), "RTO_DELIVERED", "TERMINAL")
    await db_session.commit()
    
    records = [
        {"external_order_id": "EX-OLD", "order_date": "2026-08-10", "status": "PACK", "items": []}, # Existing Out of window
        {"external_order_id": "NEW-OLD", "order_date": "2026-08-10", "status": "PRINT", "items": []}, # New Out of window
    ]
    
    # Valid coverage
    summary = await orchestrator.reconcile_report(records, date(2026, 8, 10), date(2026, 8, 19))
    
    assert summary.out_of_window_rows == 2
    
    # Check NO transition for EX-OLD
    stmt_hist = select(OrderStateTransitionModel).where(OrderStateTransitionModel.order_id == order2.id)
    hists = (await db_session.execute(stmt_hist)).scalars().all()
    assert len(hists) == 0
    
    # Check NO order for NEW-OLD
    stmt = select(SalesOrderModel).where(SalesOrderModel.external_order_id == "NEW-OLD")
    new_orders = (await db_session.execute(stmt)).scalars().all()
    assert len(new_orders) == 0

@pytest.mark.asyncio
async def test_j_and_k_invalid_rows(setup_dependencies):
    orchestrator = setup_dependencies["orchestrator"]
    
    records = [
        {"external_order_id": "", "order_date": "2026-08-18", "status": "PRINT", "items": []},
        {"external_order_id": "INV-2", "order_date": "invalid-date", "status": "PRINT", "items": []},
        {"external_order_id": "INV-3", "order_date": "2026-08-18", "status": "UNKNOWN_GARBAGE", "items": []},
    ]
    
    summary = await orchestrator.reconcile_report(records, date(2026, 8, 18), date(2026, 8, 19))
    assert summary.import_exceptions == 3

@pytest.mark.asyncio
async def test_l_report_coverage_too_short(setup_dependencies):
    orchestrator = setup_dependencies["orchestrator"]
    db_session = setup_dependencies["db_session"]
    
    order = create_mock_order(db_session, "EX-ACTIVE", date(2026, 8, 15), "PRINT", "ACTIVE")
    await db_session.commit()
    
    records = []
    
    # Required is 15-Aug to 19-Aug. We provide 16-Aug to 19-Aug.
    with pytest.raises(ValueError, match="Report coverage insufficient"):
        await orchestrator.reconcile_report(records, date(2026, 8, 16), date(2026, 8, 19))

@pytest.mark.asyncio
async def test_p_rollback_on_failure(setup_dependencies):
    orchestrator = setup_dependencies["orchestrator"]
    db_session = setup_dependencies["db_session"]
    
    records = [
        {"external_order_id": "FAIL-1", "order_date": "2026-08-18", "status": "PRINT", "items": []},
    ]
    
    # We'll monkeypatch lifecycle_engine to throw exception
    original_process = orchestrator.lifecycle_engine.process_shopdeck_status_update
    
    async def mock_process(*args, **kwargs):
        raise RuntimeError("Simulated failure")
        
    orchestrator.lifecycle_engine.process_shopdeck_status_update = mock_process
    
    summary = await orchestrator.reconcile_report(records, date(2026, 8, 18), date(2026, 8, 19))
    assert summary.import_exceptions == 1
    
    # Verify no partial order
    stmt = select(SalesOrderModel).where(SalesOrderModel.external_order_id == "FAIL-1")
    orders = (await db_session.execute(stmt)).scalars().all()
    assert len(orders) == 0

@pytest.mark.asyncio
async def test_q_inventory_immutability(setup_dependencies):
    orchestrator = setup_dependencies["orchestrator"]
    db_session = setup_dependencies["db_session"]
    
    initial_movements = await get_inventory_movements_count(db_session)
    
    records = [
        {"external_order_id": "Q-1", "order_date": "2026-08-18", "status": "DELIVERED", "items": []},
    ]
    summary = await orchestrator.reconcile_report(records, date(2026, 8, 18), date(2026, 8, 19))
    assert summary.new_shopdeck_orders == 1
    
    final_movements = await get_inventory_movements_count(db_session)
    assert initial_movements == final_movements
    assert summary.inventory_movements_created == 0
