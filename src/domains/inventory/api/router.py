from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Callable, AsyncContextManager
from dependency_injector.wiring import Provide, inject

from src.foundation.api.responses import SuccessResponse
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.models.sku import SKUModel
from src.app.container import DomainsContainer

router = APIRouter(prefix="/inventory", tags=["inventory"])

from src.domains.inventory.models.balance import InventoryBalanceModel
from src.domains.masters.models.product import ProductModel

@router.get("/balances", response_model=SuccessResponse[List[Dict[str, Any]]])
@inject
async def get_inventory_balances(
    session_factory: Callable[..., AsyncContextManager[AsyncSession]] = Depends(Provide[DomainsContainer.core.db.provided._session_factory])
):
    # Fetch all canonical balances, warehouses, and SKUs
    stmt = select(
        WarehouseModel.warehouse_name,
        SKUModel.id.label("sku_id"),
        SKUModel.sku_code,
        ProductModel.product_name.label("sku_name"),
        InventoryBalanceModel.quantity_on_hand,
        InventoryBalanceModel.confidence_score
    ).join(WarehouseModel, WarehouseModel.id == InventoryBalanceModel.warehouse_id)\
     .join(SKUModel, SKUModel.id == InventoryBalanceModel.sku_id)\
     .join(ProductModel, ProductModel.id == SKUModel.product_id)
     
    async with session_factory() as session:
        result = await session.execute(stmt)
        records = result.all()
    
    # Map to frontend structure
    response_data = []
    for r in records:
        response_data.append({
            "sku_id": str(r.sku_id),
            "warehouse": r.warehouse_name,
            "sku_code": r.sku_code,
            "sku_name": r.sku_name,
            "balance": r.quantity_on_hand,
            "confidence_score": r.confidence_score,
            "in_transit": 0 # Future capability
        })
        
    return SuccessResponse(data=response_data)

from src.domains.inventory.schemas.ledger import InventoryLedgerResponse
from src.domains.inventory.services.ledger_service import InventoryLedgerService
from uuid import UUID

@router.get("/ledger/{sku_id}", response_model=SuccessResponse[InventoryLedgerResponse])
@inject
async def get_inventory_ledger(
    sku_id: UUID,
    ledger_service: InventoryLedgerService = Depends(Provide[DomainsContainer.inventory.ledger_service])
):
    """
    Returns the full chronological history of inventory movements and running balances for a specific SKU.
    """
    ledger = await ledger_service.generate_ledger(sku_id)
    return SuccessResponse(data=ledger)

from src.domains.inventory.services.confidence_engine import ConfidenceEngine
from src.domains.inventory.schemas.confidence import InventoryConfidenceResponse

@router.get("/confidence/{sku_id}", response_model=SuccessResponse[InventoryConfidenceResponse])
@inject
async def get_inventory_confidence(
    sku_id: UUID,
    confidence_engine: ConfidenceEngine = Depends(Provide[DomainsContainer.inventory.confidence_engine])
):
    """
    Returns the calculated inventory confidence score and explainable indicators for a specific SKU.
    """
    confidence = await confidence_engine.calculate_confidence(sku_id)
    return SuccessResponse(data=confidence)
