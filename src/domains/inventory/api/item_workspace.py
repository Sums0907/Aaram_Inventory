from uuid import UUID
from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import require_permission

from src.foundation.api.responses import SuccessResponse
from src.app.container import DomainsContainer
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.masters.repositories.sku import SKURepository
from src.domains.masters.repositories.bom import BOMRepository

router = APIRouter(prefix="/inventory/items", tags=["inventory-items"])

@router.get("/{sku_id}/workspace", response_model=SuccessResponse[dict])
@inject
async def get_item_workspace(
    sku_id: UUID,
    sku_repository: SKURepository = Depends(Provide[DomainsContainer.masters.sku_repository]),
    bom_repository: BOMRepository = Depends(Provide[DomainsContainer.masters.bom_repository]),
    movement_repository: InventoryMovementRepository = Depends(Provide[DomainsContainer.inventory.movement_repository]),
    balance_repository: InventoryBalanceRepository = Depends(Provide[DomainsContainer.inventory.balance_repository]),
    _=Depends(require_permission("INVENTORY_PRODUCT_VIEW"))
):
    # 1. Identity
    sku = await sku_repository.get_by_id(sku_id)
    if not sku:
        return SuccessResponse(data=None) # Handle error appropriately in production

    # 2. Current Inventory
    from sqlalchemy import select
    from src.domains.inventory.models.balance import InventoryBalanceModel
    stmt = select(InventoryBalanceModel).where(InventoryBalanceModel.sku_id == sku_id)
    res = await balance_repository.session.execute(stmt)
    balances = res.scalars().all()
    total_stock = sum([float(b.quantity_on_hand) for b in balances])
    stock_status = "Healthy"
    if total_stock < 0:
        stock_status = "Negative"
    elif total_stock <= 10:
        stock_status = "Low"
        
    # 3. Recent Activity
    movements = await movement_repository.get_movements_for_sku(sku_id)
    recent_activity = [
        {
            "id": str(m.id),
            "movement_type": m.movement_type,
            "quantity": float(m.quantity),
            "created_on": m.created_on.isoformat()
        } for m in sorted(movements, key=lambda x: x.created_on, reverse=True)[:10]
    ]
    
    # 4. BOM Usage
    boms = await bom_repository.get_by_target_item_id(sku_id)
    bom_data = []
    if boms:
        bom = boms[0] # Just take first active BOM
        for comp in bom.components:
            comp_sku = await sku_repository.get_by_id(comp.component_item_id)
            bom_data.append({
                "component_name": comp_sku.product.product_name if comp_sku and comp_sku.product else "Unknown",
                "quantity": float(comp.quantity_per_unit),
                "uom": comp_sku.uom.short_name if comp_sku and comp_sku.uom else ""
            })

    return SuccessResponse(data={
        "identity": {
            "name": sku.product.product_name,
            "code": sku.item_code,
            "type": sku.product.item_type,
            "category": sku.product.product_type,
            "subcategory": sku.product.brand,
            "uom": sku.uom.unit_name if sku.uom else None,
            "uom_symbol": sku.uom.short_name if sku.uom else None
        },
        "inventory": {
            "stock": total_stock,
            "status": stock_status
        },
        "recent_activity": recent_activity,
        "bom_usage": bom_data
    })
