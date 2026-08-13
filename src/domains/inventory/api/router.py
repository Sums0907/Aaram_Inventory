from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, literal_column
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
    # Fetch all canonical warehouses and SKUs, left join balances
    stmt = select(
        WarehouseModel.warehouse_name,
        WarehouseModel.id.label("warehouse_id"),
        SKUModel.id.label("sku_id"),
        SKUModel.sku_code,
        ProductModel.product_name.label("sku_name"),
        InventoryBalanceModel.quantity_on_hand,
        InventoryBalanceModel.confidence_score
    ).select_from(SKUModel)\
     .join(ProductModel, ProductModel.id == SKUModel.product_id)\
     .join(WarehouseModel, literal_column("1") == literal_column("1"))\
     .outerjoin(
         InventoryBalanceModel,
         (InventoryBalanceModel.sku_id == SKUModel.id) & 
         (InventoryBalanceModel.warehouse_id == WarehouseModel.id)
     )
     
    async with session_factory() as session:
        result = await session.execute(stmt)
        records = result.all()
    
    # Map to frontend structure
    response_data = []
    for r in records:
        response_data.append({
            "sku_id": str(r.sku_id),
            "warehouse_id": str(r.warehouse_id),
            "warehouse": r.warehouse_name,
            "sku_code": r.sku_code,
            "sku_name": r.sku_name,
            "balance": r.quantity_on_hand or 0,
            "confidence_score": r.confidence_score or 50,
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

from src.domains.inventory.repositories.job_work import JobWorkRepository

@router.get("/position", response_model=SuccessResponse[List[Dict[str, Any]]])
@inject
async def get_inventory_position(
    session_factory: Callable[..., AsyncContextManager[AsyncSession]] = Depends(Provide[DomainsContainer.core.db.provided._session_factory]),
    job_work_repo: JobWorkRepository = Depends(Provide[DomainsContainer.inventory.job_work_repository])
):
    """
    Returns the full inventory position including warehouse stock and job worker pending stock,
    aggregated per SKU.
    """
    # 1. Fetch all warehouse balances
    stmt = select(
        SKUModel.id.label("sku_id"),
        InventoryBalanceModel.quantity_on_hand,
    ).select_from(SKUModel)\
     .outerjoin(
         InventoryBalanceModel,
         (InventoryBalanceModel.sku_id == SKUModel.id)
     )
     
    async with session_factory() as session:
        result = await session.execute(stmt)
        records = result.all()
        
    # Aggregate warehouse stock per SKU
    sku_warehouse_stock: Dict[UUID, float] = {}
    for r in records:
        if r.sku_id not in sku_warehouse_stock:
            sku_warehouse_stock[r.sku_id] = 0.0
        if r.quantity_on_hand:
            sku_warehouse_stock[r.sku_id] += float(r.quantity_on_hand)
            
    # 2. Fetch all job worker pending stock
    jw_stock_summary = await job_work_repo.get_pending_stock_summary()
    
    sku_jw_stock: Dict[UUID, float] = {}
    sku_jw_details: Dict[UUID, List[dict]] = {}
    
    for row in jw_stock_summary:
        sku_id = row["item_id"]
        qty = float(row["pending_quantity"])
        
        if sku_id not in sku_jw_stock:
            sku_jw_stock[sku_id] = 0.0
            sku_jw_details[sku_id] = []
            
        sku_jw_stock[sku_id] += qty
        sku_jw_details[sku_id].append({
            "name": row["job_worker_name"],
            "stock": qty
        })
        
    # 3. Combine
    all_sku_ids = set(list(sku_warehouse_stock.keys()) + list(sku_jw_stock.keys()))
    
    response_data = []
    for sku_id in all_sku_ids:
        wh_stock = sku_warehouse_stock.get(sku_id, 0.0)
        jw_stock = sku_jw_stock.get(sku_id, 0.0)
        total = wh_stock + jw_stock
        
        # Only return items with stock
        if total > 0 or wh_stock > 0 or jw_stock > 0:
            response_data.append({
                "sku_id": str(sku_id),
                "total_stock": total,
                "warehouse_stock": wh_stock,
                "job_worker_total": jw_stock,
                "job_workers": sku_jw_details.get(sku_id, [])
            })
            
    return SuccessResponse(data=response_data)
