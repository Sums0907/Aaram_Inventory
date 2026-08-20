import asyncio
import uuid
import httpx
from datetime import datetime, timezone
from src.foundation.configuration import get_settings
from src.app.container import DomainsContainer
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.data_ingestion.models.packer_event import PackerEventModel
from sqlalchemy import select

async def run_test():
    import os
    os.environ["SHOPDECK_SALES_WAREHOUSE_CODE"] = "WH-MANUAL"
    os.environ["DATABASE_ENV"] = "test"
    settings = get_settings()
    settings.DATABASE_URL = "sqlite+aiosqlite:///./test_manual_event.db"
    
    domains_container = DomainsContainer()
    domains_container.core.config.from_dict(settings.model_dump())
    
    engine = domains_container.core.db()._engine
    
    from src.foundation.database.models import BaseModel
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)
        
    async with domains_container.core.db()._session_factory() as session:
        # Create warehouse
        wh = WarehouseModel(
            id=uuid.uuid4(),
            warehouse_code="WH-MANUAL",
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
            product_code="PROD-MANUAL-1",
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
            sku_code="SKU-MANUAL-1",
            item_code="MANUAL-1",
            barcode="BAR-MANUAL-1"
        )
        session.add(sku)
        
        await session.commit()
        
    print("Database seeded.")
    
    from src.app.main import app
    from httpx import AsyncClient
    
    app.core_container = domains_container.core
    app.domains_container = domains_container
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        event_id = str(uuid.uuid4())
        payload = {
            "event_id": event_id,
            "event_type": "PACKED",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "order_id": "ORD-MANUAL",
            "awb": "AWB-MANUAL",
            "items": [
                {"sku": "SKU-MANUAL-1", "quantity": 5}
            ]
        }
        resp = await ac.post("/api/v1/internal/webhooks/packer/events", json=payload)
        print("Webhook response:", resp.status_code, resp.json())
        
    async with domains_container.core.db()._session_factory() as session:
        events = (await session.execute(select(PackerEventModel))).scalars().all()
        print(f"Packer events: {len(events)}")
        for e in events:
            print(f"  Event: {e.event_id}, type: {e.event_type}")
            
        movements = (await session.execute(select(InventoryMovementModel))).scalars().all()
        print(f"Inventory movements: {len(movements)}")
        for m in movements:
            print(f"  Movement: {m.movement_type}, qty: {m.quantity}")

asyncio.run(run_test())
