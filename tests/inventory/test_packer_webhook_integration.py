import pytest
import uuid
import os
from httpx import AsyncClient
from datetime import datetime, timezone

from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.data_ingestion.models.packer_event import PackerEventModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.models.sku import SKUModel
from sqlalchemy import select, func
from src.app.main import app

@pytest.fixture
def test_session_factory():
    # Use the same session factory that the app uses for dependency injection during tests
    return app.core_container.db()._session_factory

from src.domains.masters.models.product import ProductModel

@pytest.fixture(autouse=True)
def setup_warehouse_env(monkeypatch):
    monkeypatch.setenv("SHOPDECK_SALES_WAREHOUSE_CODE", "WH-TEST-01")

async def setup_test_data(session):
    # Create warehouse
    wh = WarehouseModel(
        id=uuid.uuid4(),
        warehouse_code="WH-TEST-01",
        warehouse_name="Test Warehouse",
        address_line_1="123 Test St",
        city="Test City",
        state="Test State",
        pin_code="123456"
    )
    session.add(wh)

    # Create Product
    prod_id = uuid.uuid4()
    prod = ProductModel(
        id=prod_id,
        product_code="PROD-PACK-1",
        product_name="Test Product",
        item_type="FINISHED_GOODS",
        product_type="TEST",
        brand="TEST"
    )
    session.add(prod)
    
    # Create SKU
    sku_id = uuid.uuid4()
    sku = SKUModel(
        id=sku_id,
        product_id=prod_id,
        sku_code="SKU-PACK-1",
        item_code="PACK-1",
        barcode="BAR-PACK-1"
    )
    session.add(sku)
    
    await session.commit()
    return wh, sku

@pytest.mark.asyncio
async def test_packer_webhook_idempotency(async_client: AsyncClient, test_session_factory):
    async with test_session_factory() as session:
        wh, sku = await setup_test_data(session)

    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "event_type": "PACKED",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "order_id": "ORD-100",
        "awb": "AWB-100",
        "items": [
            {"sku": "SKU-PACK-1", "quantity": 2}
        ]
    }

    # First request
    resp1 = await async_client.post("/api/v1/internal/webhooks/packer/events", json=payload)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "PROCESSED"

    # Second request with same event_id
    resp2 = await async_client.post("/api/v1/internal/webhooks/packer/events", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "ALREADY_PROCESSED"

    # Verify database
    async with test_session_factory() as verify_session:
        # Should only be one event
        events = (await verify_session.execute(select(PackerEventModel).where(PackerEventModel.event_id == uuid.UUID(event_id)))).scalars().all()
        assert len(events) == 1
        
        # Should only be one movement
        movements = (await verify_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == "ORD-100"))).scalars().all()
        assert len(movements) == 1
        assert movements[0].quantity == -2

@pytest.mark.asyncio
async def test_packer_webhook_physical_cycle_validation(async_client: AsyncClient, test_session_factory):
    async with test_session_factory() as session:
        wh, sku = await setup_test_data(session)

    # First PACKED event
    event_id_1 = str(uuid.uuid4())
    payload_1 = {
        "event_id": event_id_1,
        "event_type": "PACKED",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "order_id": "ORD-200",
        "awb": "AWB-200",
        "items": [{"sku": "SKU-PACK-1", "quantity": 1}]
    }
    resp1 = await async_client.post("/api/v1/internal/webhooks/packer/events", json=payload_1)
    assert resp1.status_code == 200

    # Second PACKED event with DIFFERENT event_id (Invalid cycle without RTO)
    event_id_2 = str(uuid.uuid4())
    payload_2 = {
        "event_id": event_id_2,
        "event_type": "PACKED",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "order_id": "ORD-200",
        "awb": "AWB-201",
        "items": [{"sku": "SKU-PACK-1", "quantity": 1}]
    }
    resp2 = await async_client.post("/api/v1/internal/webhooks/packer/events", json=payload_2)
    assert resp2.status_code == 400
    assert "already been packed" in resp2.text

    # Verify only one movement was created
    async with test_session_factory() as verify_session:
        movements = (await verify_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == "ORD-200"))).scalars().all()
        assert len(movements) == 1

@pytest.mark.asyncio
async def test_packer_webhook_atomic_rollback(async_client: AsyncClient, test_session_factory):
    async with test_session_factory() as session:
        wh, sku = await setup_test_data(session)

    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "event_type": "PACKED",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "order_id": "ORD-300",
        "awb": "AWB-300",
        "items": [
            {"sku": "SKU-PACK-1", "quantity": 1},
            {"sku": "SKU-INVALID-999", "quantity": 1} # This should cause validation to fail
        ]
    }

    resp = await async_client.post("/api/v1/internal/webhooks/packer/events", json=payload)
    assert resp.status_code == 400

    # Verify nothing was persisted
    async with test_session_factory() as verify_session:
        events = (await verify_session.execute(select(PackerEventModel).where(PackerEventModel.event_id == uuid.UUID(event_id)))).scalars().all()
        assert len(events) == 0
        
        movements = (await verify_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == "ORD-300"))).scalars().all()
        assert len(movements) == 0

@pytest.mark.asyncio
async def test_packer_webhook_concurrent_duplicates(async_client: AsyncClient, test_session_factory):

    import asyncio
    async with test_session_factory() as session:
        wh, sku = await setup_test_data(session)

    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "event_type": "PACKED",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "order_id": "ORD-400",
        "awb": "AWB-400",
        "items": [
            {"sku": "SKU-PACK-1", "quantity": 3}
        ]
    }

    # Simulate two requests hitting exactly at the same time
    # This might flakily pass if SQLite serializes them fully before IntegrityError, but we test the application layer
    tasks = [
        async_client.post("/api/v1/internal/webhooks/packer/events", json=payload),
        async_client.post("/api/v1/internal/webhooks/packer/events", json=payload)
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Both should be 200, one PROCESSED and one ALREADY_PROCESSED
    statuses = []
    for resp in responses:
        if not isinstance(resp, Exception):
            assert resp.status_code == 200
            statuses.append(resp.json()["status"])
            
    assert "PROCESSED" in statuses
    # The other is either ALREADY_PROCESSED or also PROCESSED if we didn't hit concurrency issues?
    # Actually if they both inserted, one would fail IntegrityError and rollback and return ALREADY_PROCESSED.
    # So we should always have exactly one PROCESSED.
    assert statuses.count("PROCESSED") == 1
    assert statuses.count("ALREADY_PROCESSED") == 1

    # Verify database strictly has 1
    async with test_session_factory() as verify_session:
        events = (await verify_session.execute(select(PackerEventModel).where(PackerEventModel.event_id == uuid.UUID(event_id)))).scalars().all()
        assert len(events) == 1
        
        movements = (await verify_session.execute(select(InventoryMovementModel).where(InventoryMovementModel.reference_number == "ORD-400"))).scalars().all()
        assert len(movements) == 1

@pytest.mark.asyncio
async def test_packer_webhook_rto_success(async_client: AsyncClient, test_session_factory):
    async with test_session_factory() as session:
        wh, sku = await setup_test_data(session)

    # First, order must be packed
    pack_event_id = str(uuid.uuid4())
    await async_client.post("/api/v1/internal/webhooks/packer/events", json={
        "event_id": pack_event_id,
        "event_type": "PACKED",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "order_id": "ORD-RTO-1",
        "awb": "AWB-RTO-1",
        "items": [{"sku": "SKU-PACK-1", "quantity": 2}]
    })

    # Now, process RTO
    rto_event_id = str(uuid.uuid4())
    rto_payload = {
        "event_id": rto_event_id,
        "event_type": "RTO_RECEIVED",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "order_id": "ORD-RTO-1",
        "awb": "REV-AWB-1",
        "items": [{"sku": "SKU-PACK-1", "quantity": 1}] # Only 1 accepted
    }

    resp = await async_client.post("/api/v1/internal/webhooks/packer/events", json=rto_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "PROCESSED"

    async with test_session_factory() as verify_session:
        movements = (await verify_session.execute(select(InventoryMovementModel).where(
            InventoryMovementModel.reference_number == "ORD-RTO-1",
            InventoryMovementModel.movement_type == "RTO_RETURN"
        ))).scalars().all()
        assert len(movements) == 1
        assert movements[0].quantity == 1

@pytest.mark.asyncio
async def test_packer_webhook_return_without_pack_fails(async_client: AsyncClient, test_session_factory):
    async with test_session_factory() as session:
        wh, sku = await setup_test_data(session)

    ret_event_id = str(uuid.uuid4())
    ret_payload = {
        "event_id": ret_event_id,
        "event_type": "CUSTOMER_RETURN_RECEIVED",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "order_id": "ORD-RET-NO-PACK",
        "awb": "REV-AWB-2",
        "items": [{"sku": "SKU-PACK-1", "quantity": 1}]
    }

    resp = await async_client.post("/api/v1/internal/webhooks/packer/events", json=ret_payload)
    assert resp.status_code == 400
    assert "cannot be returned before being packed" in resp.text
