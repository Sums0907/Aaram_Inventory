from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any
from uuid import UUID
from dependency_injector.wiring import inject, Provide

from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.accounting.services.engine import AccountingEngineService
from src.domains.inventory.dependency_injection import InventoryContainer
from src.domains.accounting.dependency_injection import AccountingContainer

# This is a simplified router just for reading data to verify the vertical slice
read_api_router = APIRouter(prefix="/read", tags=["Read APIs"])

@read_api_router.get("/inventory/balance")
@inject
async def get_inventory_balance(
    warehouse_id: UUID,
    sku_id: UUID,
    inventory_service: InventoryMovementService = Depends(Provide[InventoryContainer.movement_service])
):
    balance = await inventory_service.get_balance(warehouse_id, sku_id)
    return {"warehouse_id": warehouse_id, "sku_id": sku_id, "balance": balance}

@read_api_router.get("/dashboard")
async def get_dashboard_summary():
    # A simple aggregation endpoint. In a real system, this would use a dedicated service
    # to query aggregate metrics.
    return {
        "status": "online",
        "message": "Dashboard APIs active. Endpoints like /inventory/balance and /journal-entries are available."
    }
