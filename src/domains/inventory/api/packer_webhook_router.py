from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
logger = logging.getLogger(__name__)

from dependency_injector.wiring import Provide, inject
from typing import Callable, AsyncContextManager

from src.app.container import DomainsContainer
from src.foundation.exceptions.base import ValidationException
from src.domains.inventory.schemas.packer_webhook import PackerEventPayload, PackerEventResponse
from src.domains.inventory.services.packer_integration import PackerIntegrationService
from src.domains.inventory.services.movement import InventoryMovementService
from src.foundation.authentication.dependencies import require_permission
from src.domains.inventory.tasks.daily_reconciliation import run_daily_sku_reconciliation

router = APIRouter(prefix="/internal/webhooks/packer", tags=["Packer Integration"])

@router.post("/force-sync", status_code=status.HTTP_200_OK)
@inject
async def force_packer_sync(
    _=Depends(require_permission("INVENTORY_CATALOG_VIEW")),
    session_factory: Callable[..., AsyncContextManager[AsyncSession]] = Depends(Provide[DomainsContainer.core.db.provided._session_factory])
):
    """
    Forces an immediate generation of the Master Data and Stock Balance outbox events for AaramPacking.
    """
    try:
        async with session_factory() as db:
            async with db.begin():
                await run_daily_sku_reconciliation(db)
        return {"status": "SUCCESS", "message": "Sync successfully dispatched to outbox."}
    except Exception as e:
        logger.exception("Failed to run forced packer sync")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during sync")


@router.post("/events", response_model=PackerEventResponse, status_code=status.HTTP_200_OK)
@inject
async def handle_packer_event(
    payload: PackerEventPayload,
    session_factory: Callable[..., AsyncContextManager[AsyncSession]] = Depends(Provide[DomainsContainer.core.db.provided._session_factory]),
    mov_service: InventoryMovementService = Depends(Provide[DomainsContainer.inventory.movement_service])
):
    try:
        packer_service = PackerIntegrationService(mov_service)
        async with session_factory() as db:
            async with db.begin():
                result = await packer_service.process_packer_event(payload, db)

            
        return PackerEventResponse(
            event_id=payload.event_id,
            status=result["status"]
        )
    except ValidationException as e:
        logger.warning(f"Packer event validation failed: {str(e)}")
        # We roll back and return 400 for validation errors (e.g. invalid physical cycle or missing SKU)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        logger.error(f"Configuration error during packer event: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error processing packer event {payload.event_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
