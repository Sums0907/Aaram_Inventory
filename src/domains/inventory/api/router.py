from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from dependency_injector.wiring import Provide, inject

from src.foundation.api.responses import SuccessResponse
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.models.sku import SKUModel
from src.app.container import DomainsContainer

router = APIRouter(prefix="/inventory", tags=["inventory"])

from typing import Callable, AsyncContextManager

@router.get("/balances", response_model=SuccessResponse[List[Dict[str, Any]]])
@inject
async def get_inventory_balances(
    session_factory: Callable[..., AsyncContextManager[AsyncSession]] = Depends(Provide[DomainsContainer.core.db.provided._session_factory])
):
    # Fetch all movements, warehouses, and SKUs
    # A simple aggregation for the frontend
    stmt = select(
        WarehouseModel.warehouse_name,
        SKUModel.sku_code,
        SKUModel.sku_name,
        InventoryMovementModel.quantity,
        InventoryMovementModel.movement_type
    ).join(WarehouseModel, WarehouseModel.id == InventoryMovementModel.warehouse_id)\
     .join(SKUModel, SKUModel.id == InventoryMovementModel.sku_id)
     
    async with session_factory() as session:
        result = await session.execute(stmt)
        records = result.all()
    
    # Aggregate balances
    balances = {}
    for r in records:
        key = f"{r.warehouse_name}|{r.sku_code}|{r.sku_name}"
        if key not in balances:
            balances[key] = {"warehouse": r.warehouse_name, "sku_code": r.sku_code, "sku_name": r.sku_name, "balance": 0, "in_transit": 0}
            
        if r.movement_type == "IN":
            balances[key]["balance"] += r.quantity
        elif r.movement_type == "OUT":
            balances[key]["balance"] -= r.quantity
        elif r.movement_type == "RESERVED":
            balances[key]["in_transit"] += r.quantity
            
    response_data = list(balances.values())
    return SuccessResponse(data=response_data)
