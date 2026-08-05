import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject

from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.app.container import DomainsContainer

router = APIRouter(tags=["ShopDeck Connector"])

@router.post("/sync", response_model=SuccessResponse[Dict[str, Any]])
@inject
async def sync_shopdeck(
    current_user: CurrentUser = Depends(get_current_user),
    shopdeck_sync_service = Depends(Provide[DomainsContainer.connectors.shopdeck_sync_service])
):
    """
    Triggers a synchronization event for ShopDeck.
    """
    result = await shopdeck_sync_service.run_sync(uuid.UUID(current_user.id))
    return SuccessResponse(data=result)

@router.get("/status", response_model=SuccessResponse[Dict[str, Any]])
@inject
async def get_shopdeck_status(
    current_user: CurrentUser = Depends(get_current_user)
):
    return SuccessResponse(data={"status": "CONNECTED"})

@router.get("/history", response_model=SuccessResponse[Dict[str, Any]])
@inject
async def get_shopdeck_history(
    current_user: CurrentUser = Depends(get_current_user)
):
    return SuccessResponse(data={"history": []})

@router.get("/reports", response_model=SuccessResponse[Dict[str, Any]])
@inject
async def get_shopdeck_reports(
    current_user: CurrentUser = Depends(get_current_user)
):
    return SuccessResponse(data={"reports": []})
