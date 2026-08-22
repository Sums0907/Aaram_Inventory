import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.inventory.models.outbox import InventoryOutboundEventModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.category import CategoryModel
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.foundation.enums import ItemType
from uuid_extensions import uuid7

logger = logging.getLogger(__name__)

async def run_daily_sku_reconciliation(session):
    """
    Background task to generate a full snapshot of all FINISHED_GOODS SKUs.
    This creates a single SKU_MASTER_SNAPSHOT_SYNC event in the outbox.
    """
    logger.info("Starting Daily SKU Reconciliation for Packer Sync...")
    
    # Fetch all finished goods SKUs with their related products and categories
    stmt = select(SKUModel).join(
        ProductModel, SKUModel.product_id == ProductModel.id
    ).options(
        selectinload(SKUModel.product).selectinload(ProductModel.category),
        selectinload(SKUModel.images)
    ).where(
        ProductModel.item_type == ItemType.FINISHED_GOODS
    )
    
    result = await session.execute(stmt)
    skus = result.scalars().all()
    
    payload_items = []
    for sku in skus:
        # Safely extract category
        cat_code = ""
        if sku.product and sku.product.category:
            cat_code = sku.product.category.category_code
            
        payload_items.append({
            "inventory_sku_id": sku.item_code,
            "sku_code": sku.shopdeck_sku_id or sku.sku_code,
            "barcode": sku.barcode,
            "name": sku.product.product_name if sku.product else "",
            "category": cat_code,
            "variant": None,
            "size": sku.size,
            "color": sku.color,
            "status": sku.status.value if hasattr(sku.status, 'value') else str(sku.status),
            "image_url": next((i.image_url for i in sku.images if i.display_order == 0), None),
        })
        
    event = InventoryOutboundEventModel(
        event_id=f"evt_{uuid7()}",
        event_type="SKU_MASTER_SNAPSHOT_SYNC",
        aggregate_type="SKU_SNAPSHOT",
        aggregate_id="DAILY_SNAPSHOT",
        payload_json={"snapshot": payload_items, "count": len(payload_items)},
        status="PENDING"
    )
    
    session.add(event)

    # 2. Dispatch STOCK_BALANCE_CHANGED for all SKUs using the global balance
    movement_repo = InventoryMovementRepository(session)
    for sku in skus:
        global_qty = await movement_repo.get_global_balance(sku.id)
        stock_payload = {
            "inventory_sku_id": sku.item_code,
            "available_qty": float(global_qty),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        stock_event = InventoryOutboundEventModel(
            event_id=f"evt_{uuid7()}",
            event_type="STOCK_BALANCE_CHANGED",
            aggregate_type="SKU_STOCK",
            aggregate_id=sku.item_code,
            payload_json=stock_payload,
            status="PENDING"
        )
        session.add(stock_event)

    await session.commit()
    
    logger.info(f"Daily SKU Reconciliation complete. Dispatched Master Sync and {len(skus)} Stock Sync events.")
