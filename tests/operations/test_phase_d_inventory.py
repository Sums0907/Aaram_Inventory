import pytest
import pytest_asyncio
import os
from uuid import uuid4
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domains.operations.models.sales_order import SalesOrderModel, SalesOrderItemModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.operations.schemas.lifecycle import ShopDeckStatus
from src.app.main import app

@pytest_asyncio.fixture
async def setup_d_data(db_session: AsyncSession):
    sku = SKUModel(id=uuid4(), item_code=f"TEST-ITEM-{uuid4()}", sku_code=f"TEST-SKU-{uuid4()}", product_id=uuid4())
    db_session.add(sku)
    
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
    
    orchestrator = app.domains_container.operations.reconciliation_orchestrator(session=db_session)
    # We must also override session for its dependencies
    orchestrator.window_service.session = db_session
    orchestrator.lifecycle_engine.session = db_session
    orchestrator.movement_service.repository.session = db_session
    orchestrator.movement_service.balance_calculator.balance_repository.session = db_session
    orchestrator.movement_service.balance_calculator.movement_repository.session = db_session
    orchestrator.movement_service.balance_calculator.exception_repository.session = db_session
    
    return {"sku": sku, "warehouse": warehouse, "orchestrator": orchestrator}

@pytest.mark.asyncio
async def test_first_obs_intransit_infers_pack(setup_d_data, db_session):
    orchestrator = setup_d_data["orchestrator"]
    sku = setup_d_data["sku"]
    
    record = {
        "external_order_id": f"ORD-{uuid4()}",
        "order_date": date.today(),
        "status": "IN-TRANSIT",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 2, "unit_price": 100.0, "tax_amount": 0.0}]
    }
    
    summary = await orchestrator.reconcile_report([record], date.today(), date.today())
    assert summary.inventory_movements_created == 1
    
    movs = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == record["external_order_id"]))).scalars().all()
    assert len(movs) == 1
    assert movs[0].movement_type == "SALES_FULFILLMENT"
    assert movs[0].quantity == -2

@pytest.mark.asyncio
async def test_first_obs_expired_awb_infers_prior_outbound(setup_d_data, db_session):
    orchestrator = setup_d_data["orchestrator"]
    sku = setup_d_data["sku"]
    
    record = {
        "external_order_id": f"ORD-{uuid4()}",
        "order_date": date.today(),
        "status": "EXPIRED AWB",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 3, "unit_price": 100.0, "tax_amount": 0.0}]
    }
    
    summary = await orchestrator.reconcile_report([record], date.today(), date.today())
    assert summary.inventory_movements_created == 2
    
    movs = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == record["external_order_id"]).order_by(InventoryMovementModel.created_on))).scalars().all()
    assert len(movs) == 2
    assert movs[0].movement_type == "SALES_FULFILLMENT"
    assert movs[0].quantity == -3
    assert movs[1].movement_type == "RTO_RETURN"
    assert movs[1].quantity == 3

@pytest.mark.asyncio
async def test_rto_initiated_and_delivered(setup_d_data, db_session):
    orchestrator = setup_d_data["orchestrator"]
    sku = setup_d_data["sku"]
    ord_id = f"ORD-{uuid4()}"
    
    # 1. RTO_INITIATED -> Expect outbound PACK if not exists, and sets expectation flag, but NO RTO movement yet
    record1 = {
        "external_order_id": ord_id, "order_date": date.today(), "status": "RTO_INITIATED",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 1, "unit_price": 100.0, "tax_amount": 0.0}]
    }
    await orchestrator.reconcile_report([record1], date.today(), date.today())
    
    order = (await db_session.execute(select(SalesOrderModel).where(SalesOrderModel.external_order_id == ord_id))).scalars().first()
    assert order.has_open_rto_expectation is True
    
    movs = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == ord_id))).scalars().all()
    assert len(movs) == 1
    assert movs[0].movement_type == "SALES_FULFILLMENT" # Infers PACK
    
    # 2. RTO_DELIVERED -> Sets RTO expectation to false, creates RTO_RETURN movement
    record2 = {
        "external_order_id": ord_id, "order_date": date.today(), "status": "RTO_DELIVERED",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 1, "unit_price": 100.0, "tax_amount": 0.0}]
    }
    await orchestrator.reconcile_report([record2], date.today(), date.today())
    
    await db_session.refresh(order)
    assert order.has_open_rto_expectation is False
    
    movs2 = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == ord_id))).scalars().all()
    assert len(movs2) == 2
    inbounds = [m for m in movs2 if m.movement_type == "RTO_RETURN"]
    assert len(inbounds) == 1
    assert inbounds[0].quantity == 1

@pytest.mark.asyncio
async def test_customer_return(setup_d_data, db_session):
    orchestrator = setup_d_data["orchestrator"]
    sku = setup_d_data["sku"]
    ord_id = f"ORD-{uuid4()}"
    
    # Return Created Date only -> Expectation only, NO inventory movement
    record1 = {
        "external_order_id": ord_id, "order_date": date.today(), "status": "DELIVERED",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 1, "unit_price": 100.0, "tax_amount": 0.0}],
        "return_created_date": "2026-08-19"
    }
    await orchestrator.reconcile_report([record1], date.today(), date.today())
    
    order = (await db_session.execute(select(SalesOrderModel).where(SalesOrderModel.external_order_id == ord_id))).scalars().first()
    assert order.has_open_return_expectation is True
    
    movs = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == ord_id))).scalars().all()
    assert len(movs) == 1
    assert movs[0].movement_type == "SALES_FULFILLMENT"
    
    # Return Delivered Date -> Expectation closed, CUSTOMER_RETURN movement created
    # Status is explicitly kept as DELIVERED to prove independence from RETURNED status
    record2 = {
        "external_order_id": ord_id, "order_date": date.today(), "status": "DELIVERED",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 1, "unit_price": 100.0, "tax_amount": 0.0}],
        "return_created_date": "2026-08-19",
        "return_delivered_date": "2026-08-20"
    }
    await orchestrator.reconcile_report([record2], date.today(), date.today())
    
    await db_session.refresh(order)
    assert order.has_open_return_expectation is False
    assert order.return_delivered_date == date(2026, 8, 20)
    
    movs2 = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == ord_id))).scalars().all()
    assert len(movs2) == 2
    inbounds = [m for m in movs2 if m.movement_type == "CUSTOMER_RETURN"]
    assert len(inbounds) == 1
    assert inbounds[0].quantity == 1

@pytest.mark.asyncio
async def test_neutral_statuses_no_movements(setup_d_data, db_session):
    orchestrator = setup_d_data["orchestrator"]
    sku = setup_d_data["sku"]
    ord_id = f"ORD-{uuid4()}"
    
    record = {
        "external_order_id": ord_id, "order_date": date.today(), "status": "PENDING",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 1, "unit_price": 100.0, "tax_amount": 0.0}]
    }
    
    await orchestrator.reconcile_report([record], date.today(), date.today())
    
    movs = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == ord_id))).scalars().all()
    assert len(movs) == 0

@pytest.mark.asyncio
async def test_multi_sku_quantities(setup_d_data, db_session):
    orchestrator = setup_d_data["orchestrator"]
    sku1 = setup_d_data["sku"]
    
    sku2 = SKUModel(id=uuid4(), item_code=f"TEST-ITEM-2", sku_code=f"TEST-SKU-2", product_id=uuid4())
    db_session.add(sku2)
    await db_session.commit()
    
    ord_id = f"ORD-{uuid4()}"
    
    record = {
        "external_order_id": ord_id, "order_date": date.today(), "status": "PACK",
        "items": [
            {"external_sku_code": sku1.sku_code, "quantity": 2, "unit_price": 100.0, "tax_amount": 0.0},
            {"external_sku_code": sku2.sku_code, "quantity": 3, "unit_price": 150.0, "tax_amount": 0.0}
        ]
    }
    
    await orchestrator.reconcile_report([record], date.today(), date.today())
    
    movs = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == ord_id))).scalars().all()
    assert len(movs) == 2
    assert any(m.sku_id == sku1.id and m.quantity == -2 for m in movs)
    assert any(m.sku_id == sku2.id and m.quantity == -3 for m in movs)

@pytest.mark.asyncio
async def test_duplicate_report_inventory_idempotency(setup_d_data, db_session):
    orchestrator = setup_d_data["orchestrator"]
    sku = setup_d_data["sku"]
    ord_id = f"ORD-{uuid4()}"
    
    record = {
        "external_order_id": ord_id, "order_date": date.today(), "status": "PACK",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 1, "unit_price": 100.0, "tax_amount": 0.0}],
        "observed_at": "2026-08-18T12:00:00"
    }
    
    # Process twice
    await orchestrator.reconcile_report([record], date.today(), date.today())
    await orchestrator.reconcile_report([record], date.today(), date.today())
    
    movs = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == ord_id))).scalars().all()
    # It must be exactly 1 movement, not 2
    assert len(movs) == 1

@pytest.mark.asyncio
async def test_warehouse_determination_error_if_missing(setup_d_data, db_session):
    orchestrator = setup_d_data["orchestrator"]
    sku = setup_d_data["sku"]
    ord_id = f"ORD-{uuid4()}"
    
    # Delete the warehouse env var
    del os.environ["SHOPDECK_SALES_WAREHOUSE_CODE"]
    
    record = {
        "external_order_id": ord_id, "order_date": date.today(), "status": "PACK",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 1, "unit_price": 100.0, "tax_amount": 0.0}]
    }
    
    # It shouldn't crash entirely but it should fail to process the row and log an import_exception
    # Wait, it actually raises ValueError directly when reading the config.
    import pytest
    with pytest.raises(ValueError, match="SHOPDECK_SALES_WAREHOUSE_CODE environment variable is not configured."):
        await orchestrator.reconcile_report([record], date.today(), date.today())
    
    movs = (await db_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == ord_id))).scalars().all()
    assert len(movs) == 0
    
    # Restore for other tests
    os.environ["SHOPDECK_SALES_WAREHOUSE_CODE"] = "WH-01"

@pytest.mark.asyncio
async def test_inventory_movement_failure_rollback(setup_d_data, db_session):
    from unittest.mock import patch
    
    orchestrator = setup_d_data["orchestrator"]
    sku = setup_d_data["sku"]
    ord_id = f"ORD-{uuid4()}"
    
    record = {
        "external_order_id": ord_id, "order_date": date.today(), "status": "PACK",
        "items": [{"external_sku_code": sku.sku_code, "quantity": 1, "unit_price": 100.0, "tax_amount": 0.0}],
        "return_created_date": "2026-08-19" # Sets expectation
    }
    
    # We patch create_movement to fail, simulating a DB or validation error during movement creation.
    with patch.object(orchestrator.movement_service, "create_movement", side_effect=Exception("Simulated Inventory Failure")):
        summary = await orchestrator.reconcile_report([record], date.today(), date.today())
    
    # It should have caught the exception and logged it as an import_exception
    assert summary.import_exceptions == 1
    
    # VERIFY WITH A COMPLETELY FRESH SESSION that nothing was committed
    from tests.conftest import TestingSessionLocal
    from src.domains.operations.models.lifecycle import OrderStateTransitionModel
    
    async with TestingSessionLocal() as fresh_session:
        # 1. No SalesOrder
        order = (await fresh_session.execute(select(SalesOrderModel).where(SalesOrderModel.external_order_id == ord_id))).scalars().first()
        assert order is None, "SalesOrder should not exist"
        
        # 2. No lifecycle transition
        hists = (await fresh_session.execute(select(OrderStateTransitionModel).where(OrderStateTransitionModel.external_order_id == ord_id))).scalars().all()
        assert len(hists) == 0, "No state transitions should exist"
        
        # 3. No InventoryMovement
        movs = (await fresh_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == ord_id))).scalars().all()
        assert len(movs) == 0, "No inventory movements should exist"
