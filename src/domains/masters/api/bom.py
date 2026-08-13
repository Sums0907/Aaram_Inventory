from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
import uuid
from typing import List

from src.foundation.api.responses import SuccessResponse
from src.domains.masters.dependency_injection import MastersContainer
from src.domains.masters.services.bom import BOMService
from src.domains.masters.schemas.bom import (
    BOMCreate,
    BOMResponse
)

router = APIRouter(prefix="/boms", tags=["masters-boms"])

@router.post("", response_model=SuccessResponse[BOMResponse])
@inject
async def create_bom(
    request: BOMCreate,
    service: BOMService = Depends(Provide[MastersContainer.bom_service])
):
    sys_user = uuid.UUID("00000000-0000-0000-0000-000000000001")
    bom = await service.create_bom(request, sys_user)
    return SuccessResponse(data=bom)

@router.get("/{bom_id}", response_model=SuccessResponse[BOMResponse])
@inject
async def get_bom(
    bom_id: uuid.UUID,
    service: BOMService = Depends(Provide[MastersContainer.bom_service])
):
    bom = await service.get_bom(bom_id)
    return SuccessResponse(data=bom)

@router.get("", response_model=SuccessResponse[List[BOMResponse]])
@inject
async def get_all_boms(
    service: BOMService = Depends(Provide[MastersContainer.bom_service])
):
    boms = await service.get_all()
    return SuccessResponse(data=boms)

@router.post("/{bom_id}/archive", response_model=SuccessResponse[bool])
@inject
async def archive_bom(
    bom_id: uuid.UUID,
    service: BOMService = Depends(Provide[MastersContainer.bom_service])
):
    success = await service.archive_bom(bom_id)
    return SuccessResponse(data=success)

@router.post("/{bom_id}/restore", response_model=SuccessResponse[bool])
@inject
async def restore_bom(
    bom_id: uuid.UUID,
    service: BOMService = Depends(Provide[MastersContainer.bom_service])
):
    success = await service.restore_bom(bom_id)
    return SuccessResponse(data=success)
