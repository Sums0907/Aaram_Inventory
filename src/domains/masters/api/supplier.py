from fastapi import APIRouter, Depends, Query, status
from uuid import UUID
from dependency_injector.wiring import Provide, inject

from src.foundation.api.responses import SuccessResponse, PaginatedResponse, PaginationMeta
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.app.container import DomainsContainer
from src.domains.masters.services.supplier import SupplierService
from src.domains.masters.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.post("", response_model=SuccessResponse[SupplierResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_supplier(
    supplier: SupplierCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: SupplierService = Depends(Provide[DomainsContainer.masters.supplier_service])
):
    user_uuid = UUID(current_user.id)
    result = await service.create(supplier, created_by=user_uuid)
    return SuccessResponse(data=SupplierResponse.model_validate(result, from_attributes=True), message="Supplier created successfully")

@router.get("", response_model=PaginatedResponse[SupplierResponse])
@inject
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    service: SupplierService = Depends(Provide[DomainsContainer.masters.supplier_service])
):
    items, total = await service.get_all(skip=skip, limit=limit)
    response_items = [SupplierResponse.model_validate(item, from_attributes=True) for item in items]
    meta = PaginationMeta(
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1
    )
    return PaginatedResponse(data=response_items, meta=meta)

@router.get("/{supplier_id}", response_model=SuccessResponse[SupplierResponse])
@inject
async def get_supplier(
    supplier_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: SupplierService = Depends(Provide[DomainsContainer.masters.supplier_service])
):
    result = await service.get_by_id(supplier_id)
    return SuccessResponse(data=SupplierResponse.model_validate(result, from_attributes=True))

@router.put("/{supplier_id}", response_model=SuccessResponse[SupplierResponse])
@inject
async def update_supplier(
    supplier_id: UUID,
    supplier: SupplierUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: SupplierService = Depends(Provide[DomainsContainer.masters.supplier_service])
):
    user_uuid = UUID(current_user.id)
    result = await service.update(supplier_id, supplier, updated_by=user_uuid)
    return SuccessResponse(data=SupplierResponse.model_validate(result, from_attributes=True), message="Supplier updated successfully")

@router.delete("/{supplier_id}", response_model=SuccessResponse[None])
@inject
async def delete_supplier(
    supplier_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: SupplierService = Depends(Provide[DomainsContainer.masters.supplier_service])
):
    await service.delete(supplier_id)
    return SuccessResponse(data=None, message="Supplier deleted successfully")
