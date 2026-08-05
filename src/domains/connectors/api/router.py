import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse

router = APIRouter(tags=["Connectors"])

# Normally we'd inject the SyncService. For the demonstration, we'll mock it or inject a skeleton.
# We will create a dependency container for the Connectors domain next.

@router.post("/{marketplace_id}/sync", response_model=SuccessResponse[Dict[str, Any]])
@inject
async def sync_marketplace(
    marketplace_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    shopdeck_sync_service = Depends(Provide["domains_container.connectors.shopdeck_sync_service"])
):
    """
    Triggers a synchronization event for a specific marketplace.
    """
    if marketplace_id.upper() != "SHOPDECK":
        raise HTTPException(status_code=400, detail="Only SHOPDECK is currently supported.")
        
    result = await shopdeck_sync_service.run_sync(uuid.UUID(current_user.id))
    
    return SuccessResponse(data=result)
