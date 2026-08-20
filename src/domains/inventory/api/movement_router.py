from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
import uuid

from src.foundation.api.responses import SuccessResponse
from src.foundation.authentication.dependencies import require_permission, CurrentUser
from src.app.container import DomainsContainer
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService

from src.domains.inventory.schemas.movement import (
    PurchaseReceiptRequest,
    PurchaseReturnRequest,
    CustomerReturnRequest,
    RTOReturnRequest,
    ManualAdjustmentRequest,
    StockCountAdjustmentRequest,
    InventoryMovementCreate,
    InventoryMovementResponse
)

from typing import Optional

router = APIRouter(prefix="/inventory/movements", tags=["inventory-operations"])

from datetime import date

@router.get("/activities")
@inject
async def get_inventory_activities(
    skip: int = 0,
    limit: int = 100,
    movement_type: Optional[str] = None,
    sku_id: Optional[uuid.UUID] = None,
    item_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    movement_service: InventoryMovementService = Depends(Provide[DomainsContainer.inventory.movement_service]),
    _=Depends(require_permission("INVENTORY_ACTIVITY_VIEW"))
):
    activities = await movement_service.get_activities(
        skip=skip, 
        limit=limit, 
        movement_type=movement_type, 
        sku_id=sku_id,
        item_type=item_type,
        date_from=date_from,
        date_to=date_to
    )
    return SuccessResponse(data=activities)


@router.post("/purchase-receipts", response_model=SuccessResponse[InventoryMovementResponse])
@inject
async def record_purchase_receipt(
    request: PurchaseReceiptRequest,
    movement_service: InventoryMovementService = Depends(Provide[DomainsContainer.inventory.movement_service]),
    balance_calculator: BalanceCalculatorService = Depends(Provide[DomainsContainer.inventory.balance_calculator]),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_RECEIPT_CREATE"))
):
    mov_create = InventoryMovementCreate(
        movement_number=f"MOV-PR-{uuid.uuid4().hex[:8].upper()}",
        movement_type="PURCHASE_RECEIPT",
        movement_date=request.receipt_date,
        posting_date=request.receipt_date,
        status="POSTED",
        warehouse_id=request.warehouse_id,
        sku_id=request.sku_id,
        quantity=request.quantity, # positive
        reference_type="VENDOR",
        reference_number=request.purchase_document,
        reference_id=request.vendor_id
    )
    # Use actual user from context
    sys_user = uuid.UUID(current_user.id)
    mov = await movement_service.create_movement(mov_create, sys_user)
    
    # Trigger recalculation
    await balance_calculator.recalculate_balance(request.warehouse_id, request.sku_id)
    
    return SuccessResponse(data=mov)


@router.post("/purchase-returns", response_model=SuccessResponse[InventoryMovementResponse])
@inject
async def record_purchase_return(
    request: PurchaseReturnRequest,
    movement_service: InventoryMovementService = Depends(Provide[DomainsContainer.inventory.movement_service]),
    balance_calculator: BalanceCalculatorService = Depends(Provide[DomainsContainer.inventory.balance_calculator]),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_RETURN_CREATE"))
):
    mov_create = InventoryMovementCreate(
        movement_number=f"MOV-PRT-{uuid.uuid4().hex[:8].upper()}",
        movement_type="PURCHASE_RETURN",
        movement_date=request.return_date,
        posting_date=request.return_date,
        status="POSTED",
        warehouse_id=request.warehouse_id,
        sku_id=request.sku_id,
        quantity=-abs(request.quantity), # explicitly negative
        reference_type="VENDOR",
        reference_number=request.purchase_document,
        reference_id=request.vendor_id
    )
    sys_user = uuid.UUID(current_user.id)
    mov = await movement_service.create_movement(mov_create, sys_user)
    await balance_calculator.recalculate_balance(request.warehouse_id, request.sku_id)
    return SuccessResponse(data=mov)


@router.post("/customer-returns", response_model=SuccessResponse[InventoryMovementResponse])
@inject
async def record_customer_return(
    request: CustomerReturnRequest,
    movement_service: InventoryMovementService = Depends(Provide[DomainsContainer.inventory.movement_service]),
    balance_calculator: BalanceCalculatorService = Depends(Provide[DomainsContainer.inventory.balance_calculator]),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_RETURN_CREATE"))
):
    mov_create = InventoryMovementCreate(
        movement_number=f"MOV-CR-{uuid.uuid4().hex[:8].upper()}",
        movement_type="CUSTOMER_RETURN",
        movement_date=request.return_date,
        posting_date=request.return_date,
        status="POSTED",
        warehouse_id=request.warehouse_id,
        sku_id=request.sku_id,
        quantity=abs(request.quantity), # explicitly positive
        reference_type="CUSTOMER",
        reference_number=request.order_number,
        reference_id=request.customer_id
    )
    sys_user = uuid.UUID(current_user.id)
    mov = await movement_service.create_movement(mov_create, sys_user)
    await balance_calculator.recalculate_balance(request.warehouse_id, request.sku_id)
    return SuccessResponse(data=mov)


@router.post("/rto-returns", response_model=SuccessResponse[InventoryMovementResponse])
@inject
async def record_rto_return(
    request: RTOReturnRequest,
    movement_service: InventoryMovementService = Depends(Provide[DomainsContainer.inventory.movement_service]),
    balance_calculator: BalanceCalculatorService = Depends(Provide[DomainsContainer.inventory.balance_calculator]),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_RETURN_CREATE"))
):
    mov_create = InventoryMovementCreate(
        movement_number=f"MOV-RTO-{uuid.uuid4().hex[:8].upper()}",
        movement_type="RTO_RETURN",
        movement_date=request.rto_date,
        posting_date=request.rto_date,
        status="POSTED",
        warehouse_id=request.warehouse_id,
        sku_id=request.sku_id,
        quantity=abs(request.quantity), # explicitly positive
        reference_type="COURIER",
        reference_number=request.awb_number,
        reference_id=request.courier_id
    )
    sys_user = uuid.UUID(current_user.id)
    mov = await movement_service.create_movement(mov_create, sys_user)
    await balance_calculator.recalculate_balance(request.warehouse_id, request.sku_id)
    return SuccessResponse(data=mov)


@router.post("/manual-adjustments", response_model=SuccessResponse[InventoryMovementResponse])
@inject
async def record_manual_adjustment(
    request: ManualAdjustmentRequest,
    movement_service: InventoryMovementService = Depends(Provide[DomainsContainer.inventory.movement_service]),
    balance_calculator: BalanceCalculatorService = Depends(Provide[DomainsContainer.inventory.balance_calculator]),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_ADJUSTMENT_CREATE"))
):
    mov_create = InventoryMovementCreate(
        movement_number=f"MOV-ADJ-{uuid.uuid4().hex[:8].upper()}",
        movement_type="MANUAL_ADJUSTMENT",
        movement_date=request.adjustment_date,
        posting_date=request.adjustment_date,
        status="POSTED",
        warehouse_id=request.warehouse_id,
        sku_id=request.sku_id,
        quantity=request.quantity, # positive or negative
        reference_type="MANUAL",
        reference_number=request.reference_number,
        # Default UUID as we don't have a specific reference ID for manual
        reference_id=uuid.UUID("00000000-0000-0000-0000-000000000000") 
    )
    sys_user = uuid.UUID(current_user.id)
    mov = await movement_service.create_movement(mov_create, sys_user)
    await balance_calculator.recalculate_balance(request.warehouse_id, request.sku_id)
    return SuccessResponse(data=mov)


@router.post("/stock-counts", response_model=SuccessResponse[InventoryMovementResponse])
@inject
async def record_stock_count(
    request: StockCountAdjustmentRequest,
    movement_service: InventoryMovementService = Depends(Provide[DomainsContainer.inventory.movement_service]),
    balance_calculator: BalanceCalculatorService = Depends(Provide[DomainsContainer.inventory.balance_calculator]),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_VERIFICATION_EXECUTE"))
):
    mov_create = InventoryMovementCreate(
        movement_number=f"MOV-STC-{uuid.uuid4().hex[:8].upper()}",
        movement_type="STOCK_COUNT_ADJUSTMENT",
        movement_date=request.count_date,
        posting_date=request.count_date,
        status="POSTED",
        warehouse_id=request.warehouse_id,
        sku_id=request.sku_id,
        quantity=request.difference, # Difference between physical and system
        reference_type="STOCK_COUNT",
        reference_number=request.stock_count_reference,
        reference_id=uuid.UUID("00000000-0000-0000-0000-000000000000") 
    )
    sys_user = uuid.UUID(current_user.id)
    mov = await movement_service.create_movement(mov_create, sys_user)
    await balance_calculator.recalculate_balance(request.warehouse_id, request.sku_id)
    return SuccessResponse(data=mov)
