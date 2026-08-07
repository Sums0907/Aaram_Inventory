from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.inventory_item import InventoryItemCreate
from src.domains.masters.schemas.sku import SKUResponse
from src.domains.masters.services.inventory_item import InventoryItemService
from src.domains.masters.dependency_injection import MastersContainer

router = APIRouter(prefix="/inventory-items", tags=["Inventory Item"])

@router.post("", response_model=SuccessResponse[SKUResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_inventory_item(
    schema: InventoryItemCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: InventoryItemService = Depends(Provide[MastersContainer.inventory_item_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    sku = await service.create_inventory_item(schema, user_id=user_uuid)
    
    await service.session.commit()
    
    # Eagerly load relationships so SKUResponse can serialize them
    # For simplicity, we just reload it with relationships
    from sqlalchemy.orm import joinedload, selectinload
    from sqlalchemy import select
    from src.domains.masters.models.sku import SKUModel
    
    result = await service.session.execute(
        select(SKUModel)
        .options(
            joinedload(SKUModel.product),
            joinedload(SKUModel.pricing),
            selectinload(SKUModel.images)
        )
        .filter(SKUModel.id == sku.id)
    )
    loaded_sku = result.scalars().first()
    
    return SuccessResponse(data=SKUResponse.model_validate(loaded_sku, from_attributes=True))
