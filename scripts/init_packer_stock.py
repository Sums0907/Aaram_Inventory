import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.foundation.configuration.settings import get_settings
from src.foundation.database.session import Database
from src.domains.masters.models.sku import SKUModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.models.outbox import InventoryOutboundEventModel
from sqlalchemy import select, func
from uuid_extensions import uuid7
from datetime import datetime, timezone

settings = get_settings()
db = Database(
    db_url=settings.DATABASE_URL,
    debug=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

async def init_packer_stock():
    # Use the session generator properly
    session_gen = db.session()
    session = await session_gen.__anext__()
    
    try:
        # Get all active SKUs
        stmt = select(SKUModel).where(SKUModel.status == "ACTIVE")
        skus = (await session.execute(stmt)).scalars().all()
        
        events = []
        for sku in skus:
            stmt_bal = select(func.sum(InventoryMovementModel.quantity)).where(
                InventoryMovementModel.sku_id == sku.id,
                InventoryMovementModel.status == "POSTED"
            )
            bal = (await session.execute(stmt_bal)).scalar()
            global_qty = float(bal) if bal is not None else 0.0
            
            payload = {
                "inventory_sku_id": str(sku.id),
                "available_qty": global_qty,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            event = InventoryOutboundEventModel(
                event_id=f"evt_{uuid7()}",
                event_type="STOCK_BALANCE_CHANGED",
                aggregate_type="SKU_STOCK",
                aggregate_id=str(sku.id),
                payload_json=payload,
                status="PENDING"
            )
            session.add(event)
            events.append(event)
            
        await session.commit()
        print(f"Injected {len(events)} STOCK_BALANCE_CHANGED events to sync global stock.")
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(init_packer_stock())
