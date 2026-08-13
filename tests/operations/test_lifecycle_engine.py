import pytest
import pytest_asyncio
from datetime import date, datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.models.lifecycle import CustomerReturnPolicyModel, OrderStateTransitionModel
from src.domains.operations.services.lifecycle_engine import LifecycleEngine, UnknownShopDeckStatusException
from src.domains.operations.schemas.lifecycle import LifecycleState, ShopDeckStatus

@pytest_asyncio.fixture
async def lifecycle_engine(db_session: AsyncSession):
    # Setup initial return policy (7 days)
    policy = CustomerReturnPolicyModel(
        id=uuid4(),
        effective_from=date(2026, 8, 1),
        return_window_days=7,
        is_active=True
    )
    db_session.add(policy)
    await db_session.commit()
    return LifecycleEngine(db_session)


@pytest_asyncio.fixture
async def base_order(db_session: AsyncSession):
    order = SalesOrderModel(
        id=uuid4(),
        external_order_id=f"TEST-{uuid4()}",
        channel="SHOPDECK",
        order_date=date(2026, 8, 10),
        status="PRINT",
        customer_name="Test User",
        shipping_address="Test Address",
        shipping_pincode="123456",
        shipping_city="Test City",
        shipping_state="Test State",
        payment_method="COD"
    )
    db_session.add(order)
    await db_session.commit()
    return order


@pytest.mark.asyncio
async def test_normal_delivery_sequence(db_session: AsyncSession, lifecycle_engine: LifecycleEngine, base_order: SalesOrderModel):
    # 1. PRINT -> PACK
    obs_date = datetime(2026, 8, 10, 10, 0)
    did_transition, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "PACK", obs_date)
    assert did_transition is True
    assert state == LifecycleState.ACTIVE
    
    # 2. PACK -> IN-TRANSIT
    obs_date += timedelta(days=1)
    did_transition, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "IN-TRANSIT", obs_date)
    assert state == LifecycleState.ACTIVE
    
    # 3. IN-TRANSIT -> HANDOVER
    obs_date += timedelta(days=1)
    did_transition, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "HANDOVER", obs_date)
    assert state == LifecycleState.ACTIVE

    # 4. HANDOVER -> DELIVERED
    obs_date += timedelta(days=1) # Aug 13
    did_transition, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "DELIVERED", obs_date)
    assert state == LifecycleState.ACTIVE
    assert base_order.return_watch_until == date(2026, 8, 20) # 13 + 7 days
    
    # Verify transitions history
    stmt = select(OrderStateTransitionModel).where(OrderStateTransitionModel.order_id == base_order.id).order_by(OrderStateTransitionModel.observed_at)
    res = await db_session.execute(stmt)
    transitions = res.scalars().all()
    assert len(transitions) == 4
    assert transitions[-1].new_status == "DELIVERED"
    
    # 5. Check expiry before window (Aug 19)
    state = lifecycle_engine._determine_lifecycle_state("DELIVERED", base_order.return_watch_until, date(2026, 8, 19))
    assert state == LifecycleState.ACTIVE

    # 6. Check expiry after window (Aug 21)
    state = lifecycle_engine._determine_lifecycle_state("DELIVERED", base_order.return_watch_until, date(2026, 8, 21))
    assert state == LifecycleState.TERMINAL


@pytest.mark.asyncio
async def test_rto_sequence(db_session: AsyncSession, lifecycle_engine: LifecycleEngine, base_order: SalesOrderModel):
    obs_date = datetime(2026, 8, 10, 10, 0)
    
    # IN-TRANSIT
    await lifecycle_engine.process_shopdeck_status_update(base_order, "IN-TRANSIT", obs_date)
    
    # RTO_ACKNOWLEDGED
    obs_date += timedelta(days=1)
    _, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "RTO_ACKNOWLEDGED", obs_date)
    assert state == LifecycleState.ACTIVE
    
    # RTO_INITIATED
    obs_date += timedelta(days=1)
    _, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "RTO_INITIATED", obs_date)
    assert state == LifecycleState.ACTIVE
    
    # RTO_DELIVERED
    obs_date += timedelta(days=1)
    _, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "RTO_DELIVERED", obs_date)
    assert state == LifecycleState.TERMINAL
    assert base_order.terminal_date == obs_date.date()


@pytest.mark.asyncio
async def test_return_after_delivery_sequence(db_session: AsyncSession, lifecycle_engine: LifecycleEngine, base_order: SalesOrderModel):
    # DELIVERED
    obs_date = datetime(2026, 8, 10, 10, 0)
    _, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "DELIVERED", obs_date)
    assert state == LifecycleState.ACTIVE

    # RETURNED
    obs_date += timedelta(days=2)
    _, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "RETURNED", obs_date)
    assert state == LifecycleState.TERMINAL


@pytest.mark.asyncio
async def test_late_rto_after_delivered(db_session: AsyncSession, lifecycle_engine: LifecycleEngine, base_order: SalesOrderModel):
    # Aug 10: DELIVERED
    obs_date = datetime(2026, 8, 10, 10, 0)
    _, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "DELIVERED", obs_date)
    assert state == LifecycleState.ACTIVE
    
    # Aug 19: RTO_INITIATED
    obs_date = datetime(2026, 8, 19, 10, 0)
    _, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "RTO_INITIATED", obs_date)
    assert state == LifecycleState.ACTIVE
    
    # Aug 20: RTO_DELIVERED
    obs_date = datetime(2026, 8, 20, 10, 0)
    _, state = await lifecycle_engine.process_shopdeck_status_update(base_order, "RTO_DELIVERED", obs_date)
    assert state == LifecycleState.TERMINAL


@pytest.mark.asyncio
async def test_policy_change_preservation(db_session: AsyncSession, lifecycle_engine: LifecycleEngine, base_order: SalesOrderModel):
    # 13 Aug Delivery under 7 day policy
    obs_date = datetime(2026, 8, 13, 10, 0)
    await lifecycle_engine.process_shopdeck_status_update(base_order, "DELIVERED", obs_date)
    assert base_order.return_watch_until == date(2026, 8, 20)
    assert base_order.return_window_days_at_delivery == 7
    
    # 1 Oct Policy changes to 10 days
    new_policy = CustomerReturnPolicyModel(
        id=uuid4(),
        effective_from=date(2026, 10, 1),
        return_window_days=10,
        is_active=True
    )
    db_session.add(new_policy)
    await db_session.commit()
    
    # Re-evaluating the old order should NOT change its watch_until
    obs_date_later = datetime(2026, 10, 2, 10, 0)
    await lifecycle_engine.process_shopdeck_status_update(base_order, "DELIVERED", obs_date_later)
    
    assert base_order.return_watch_until == date(2026, 8, 20)
    assert base_order.return_window_days_at_delivery == 7


@pytest.mark.asyncio
async def test_idempotency_duplicate_observation(db_session: AsyncSession, lifecycle_engine: LifecycleEngine, base_order: SalesOrderModel):
    obs_date = datetime(2026, 8, 10, 10, 0)
    
    # First observation
    did_trans1, _ = await lifecycle_engine.process_shopdeck_status_update(base_order, "PACK", obs_date)
    assert did_trans1 is True
    
    # Duplicate observation exactly same
    did_trans2, _ = await lifecycle_engine.process_shopdeck_status_update(base_order, "PACK", obs_date)
    assert did_trans2 is False
    
    # Duplicate observation later date, same status
    obs_date_later = datetime(2026, 8, 11, 10, 0)
    did_trans3, _ = await lifecycle_engine.process_shopdeck_status_update(base_order, "PACK", obs_date_later)
    assert did_trans3 is False # No new transition recorded because old_status == new_status
    
    stmt = select(OrderStateTransitionModel).where(OrderStateTransitionModel.order_id == base_order.id)
    res = await db_session.execute(stmt)
    assert len(res.scalars().all()) == 1


@pytest.mark.asyncio
async def test_unknown_status(db_session: AsyncSession, lifecycle_engine: LifecycleEngine, base_order: SalesOrderModel):
    obs_date = datetime(2026, 8, 10, 10, 0)
    with pytest.raises(UnknownShopDeckStatusException):
        await lifecycle_engine.process_shopdeck_status_update(base_order, "WEIRD_NEW_STATUS", obs_date)
