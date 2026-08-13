import asyncio
from httpx import AsyncClient
from src.app.main import app

async def test_window_func():
    from src.app.container import DomainsContainer
    from src.foundation.configuration import get_settings
    from sqlalchemy import select, func
    from src.domains.inventory.models.movement import InventoryMovementModel
    from src.domains.masters.models.product import SkuModel, ProductModel
    
    container = DomainsContainer()
    container.wire(modules=[__name__])
    settings = get_settings()
    container.core.config.from_dict(settings.model_dump())
    
    session_factory = container.core.db()._session_factory
    async with session_factory() as session:
        # Define CTE with running balance
        balance_col = func.sum(InventoryMovementModel.quantity).over(
            partition_by=InventoryMovementModel.sku_id,
            order_by=(InventoryMovementModel.posting_date.asc(), InventoryMovementModel.created_on.asc())
        ).label('balance_after_activity')
        
        cte = select(InventoryMovementModel, balance_col).where(InventoryMovementModel.status == "POSTED").cte('movement_cte')
        
        # Join with SKU and Product
        stmt = (
            select(
                cte.c.id,
                cte.c.movement_type,
                cte.c.movement_date,
                cte.c.posting_date,
                cte.c.quantity,
                cte.c.balance_after_activity,
                cte.c.reference_type,
                cte.c.reference_number,
                cte.c.reference_id,
                cte.c.created_on,
                SkuModel.name.label("sku_name"),
                SkuModel.barcode.label("sku_barcode"),
                ProductModel.name.label("product_name"),
                ProductModel.item_type.label("item_type")
            )
            .join(SkuModel, SkuModel.id == cte.c.sku_id)
            .join(ProductModel, ProductModel.id == SkuModel.product_id)
            .order_by(cte.c.posting_date.desc(), cte.c.created_on.desc())
            .limit(10)
        )
        
        result = await session.execute(stmt)
        rows = result.all()
        for r in rows:
            print(f"{r.movement_type} | {r.product_name} - {r.sku_name} | Qty: {r.quantity} | Bal: {r.balance_after_activity}")

if __name__ == "__main__":
    asyncio.run(test_window_func())
