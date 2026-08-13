import pytest
import pytest_asyncio
from datetime import date, datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.schemas.lifecycle import LifecycleState
from src.domains.operations.services.report_window import ShopDeckReportWindowService, DateProvider

class MockDateProvider(DateProvider):
    def __init__(self, mocked_today: date):
        self.mocked_today = mocked_today
    def today(self) -> date:
        return self.mocked_today

def create_mock_order(db_session, order_date, status, lifecycle_state, return_watch_until=None):
    order = SalesOrderModel(
        id=uuid4(),
        external_order_id=f"TEST-{uuid4()}",
        channel="SHOPDECK",
        order_date=order_date,
        status=status,
        customer_name="Test User",
        shipping_address="Test Address",
        shipping_pincode="123456",
        shipping_city="Test City",
        shipping_state="Test State",
        payment_method="COD",
        lifecycle_state=lifecycle_state,
        return_watch_until=return_watch_until
    )
    db_session.add(order)
    return order

@pytest_asyncio.fixture
async def setup_orders(db_session: AsyncSession):
    # Today is 2026-08-19
    # Terminal: RTO_DELIVERED
    order_a = create_mock_order(db_session, date(2026, 6, 1), "RTO_DELIVERED", LifecycleState.TERMINAL.value)
    
    # Terminal: DELIVERED, return_watch_until passed (Aug 12 < Aug 19)
    # Physically remains ACTIVE in DB because lifecycle engine hasn't processed it
    order_b = create_mock_order(db_session, date(2026, 6, 5), "DELIVERED", LifecycleState.ACTIVE.value, date(2026, 8, 12))
    
    # Active: HANDOVER
    order_c = create_mock_order(db_session, date(2026, 8, 15), "HANDOVER", LifecycleState.ACTIVE.value)
    
    # Active: DELIVERED, return_watch_until in future (Aug 25 >= Aug 19)
    order_d = create_mock_order(db_session, date(2026, 8, 18), "DELIVERED", LifecycleState.ACTIVE.value, date(2026, 8, 25))
    
    await db_session.commit()
    return {"A": order_a, "B": order_b, "C": order_c, "D": order_d}

@pytest.mark.asyncio
async def test_dynamic_window_oldest_active_selection(db_session: AsyncSession, setup_orders):
    # Tests A, B, C, D scenario from requirements
    date_provider = MockDateProvider(date(2026, 8, 19))
    service = ShopDeckReportWindowService(db_session, date_provider)
    
    response = await service.calculate_required_window()
    
    # Order C is the oldest TRULY active order
    order_c = setup_orders["C"]
    
    assert response.required_report_start_date == date(2026, 8, 15)
    assert response.required_report_end_date == date(2026, 8, 19)
    assert response.oldest_active_order_date == date(2026, 8, 15)
    assert response.oldest_active_order_id == str(order_c.id)
    assert response.active_order_count == 2 # C and D are active
    assert f"Order {order_c.id}" in response.reason

@pytest.mark.asyncio
async def test_boundary_return_watch_until_today(db_session: AsyncSession):
    # return_watch_until == today -> logically ACTIVE
    date_provider = MockDateProvider(date(2026, 8, 20))
    order = create_mock_order(db_session, date(2026, 8, 13), "DELIVERED", LifecycleState.ACTIVE.value, date(2026, 8, 20))
    await db_session.commit()
    
    service = ShopDeckReportWindowService(db_session, date_provider)
    response = await service.calculate_required_window()
    
    assert response.active_order_count == 1
    assert response.oldest_active_order_id == str(order.id)

@pytest.mark.asyncio
async def test_boundary_return_watch_until_past(db_session: AsyncSession):
    # return_watch_until < today -> logically TERMINAL
    date_provider = MockDateProvider(date(2026, 8, 21))
    create_mock_order(db_session, date(2026, 8, 13), "DELIVERED", LifecycleState.ACTIVE.value, date(2026, 8, 20))
    await db_session.commit()
    
    service = ShopDeckReportWindowService(db_session, date_provider)
    response = await service.calculate_required_window()
    
    assert response.active_order_count == 0
    assert response.required_report_start_date is None

@pytest.mark.asyncio
async def test_deterministic_oldest_order_selection(db_session: AsyncSession):
    date_provider = MockDateProvider(date(2026, 8, 19))
    
    order1 = create_mock_order(db_session, date(2026, 8, 10), "PRINT", LifecycleState.ACTIVE.value)
    order2 = create_mock_order(db_session, date(2026, 8, 10), "PRINT", LifecycleState.ACTIVE.value)
    await db_session.commit()
    
    service = ShopDeckReportWindowService(db_session, date_provider)
    response = await service.calculate_required_window()
    
    expected_id = str(min(order1.id, order2.id))
    assert response.oldest_active_order_id == expected_id

@pytest.mark.asyncio
async def test_late_rto_uses_order_date(db_session: AsyncSession):
    date_provider = MockDateProvider(date(2026, 8, 19))
    order = create_mock_order(db_session, date(2026, 8, 10), "RTO_INITIATED", LifecycleState.ACTIVE.value)
    # The order_date is 10-Aug. Even if event was 19-Aug (not stored in this model directly but implied)
    await db_session.commit()
    
    service = ShopDeckReportWindowService(db_session, date_provider)
    response = await service.calculate_required_window()
    
    assert response.required_report_start_date == date(2026, 8, 10)

@pytest.mark.asyncio
async def test_no_active_orders(db_session: AsyncSession):
    date_provider = MockDateProvider(date(2026, 8, 19))
    service = ShopDeckReportWindowService(db_session, date_provider)
    
    response = await service.calculate_required_window()
    
    assert response.required_report_start_date is None
    assert response.required_report_end_date is None
    assert response.active_order_count == 0
    assert "No active ShopDeck orders" in response.reason

@pytest.mark.asyncio
async def test_read_only_guarantee(db_session: AsyncSession, setup_orders):
    # Ensure no db modifications occur during service execution
    date_provider = MockDateProvider(date(2026, 8, 19))
    service = ShopDeckReportWindowService(db_session, date_provider)
    
    # Save states
    order_b_id = setup_orders["B"].id
    
    await service.calculate_required_window()
    
    # Verify state remains ACTIVE physically for Order B
    stmt = select(SalesOrderModel).where(SalesOrderModel.id == order_b_id)
    res = await db_session.execute(stmt)
    order_b = res.scalar_one()
    
    assert order_b.lifecycle_state == LifecycleState.ACTIVE.value
