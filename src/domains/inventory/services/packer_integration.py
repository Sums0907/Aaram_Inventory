import os
import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.foundation.exceptions.base import ValidationException
from src.domains.data_ingestion.models.packer_event import PackerEventModel
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.schemas.packer_webhook import PackerEventPayload
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.models.sku import SKUModel

class PackerIntegrationService:
    def __init__(self, movement_service: InventoryMovementService):
        self.movement_service = movement_service

    async def _get_warehouse_id(self, session: AsyncSession) -> uuid.UUID:
        warehouse_code = os.getenv("SHOPDECK_SALES_WAREHOUSE_CODE")
        if not warehouse_code:
            raise ValueError("SHOPDECK_SALES_WAREHOUSE_CODE environment variable is not configured.")
        
        stmt_wh = select(WarehouseModel).where(WarehouseModel.warehouse_code == warehouse_code)
        wh_res = await session.execute(stmt_wh)
        warehouse = wh_res.scalars().first()
        if not warehouse:
            raise ValueError(f"ShopDeck Sales Warehouse '{warehouse_code}' is not configured.")
        return warehouse.id

    async def _validate_physical_cycle(self, session: AsyncSession, order_id: str, event_type: str) -> None:
        """
        Validates whether the new event type is permitted given the physical event history.
        For Phase 2, we only accept the first PACKED event.
        """
        if event_type == "PACKED":
            # Check if this order has already been fulfilled
            stmt = select(InventoryMovementModel).where(
                InventoryMovementModel.reference_type == "PACKER_ORDER",
                InventoryMovementModel.reference_number == order_id,
                InventoryMovementModel.movement_type == "SALES_FULFILLMENT"
            ).limit(1)
            res = await session.execute(stmt)
            if res.scalars().first():
                # A sales fulfillment already exists for this order. 
                # Since we don't have RTO boundaries yet in Phase 2, reject a second PACKED event.
                raise ValidationException(f"Invalid physical cycle: order '{order_id}' has already been packed.")
        else:
            raise ValidationException(f"Event type '{event_type}' is not yet supported.")

    async def process_packer_event(self, payload: PackerEventPayload, session: AsyncSession) -> dict:
        """
        Processes a single Packer event. Must be called within a transaction by the router.
        """
        # 1. Idempotency Check
        stmt = select(PackerEventModel).where(PackerEventModel.event_id == payload.event_id)
        res = await session.execute(stmt)
        if res.scalars().first():
            return {"status": "ALREADY_PROCESSED"}

        # 2. Physical-cycle validation
        await self._validate_physical_cycle(session, payload.order_id, payload.event_type)

        # 3. Resolve Warehouse
        warehouse_id = await self._get_warehouse_id(session)

        # 4. Record the Event FIRST to catch concurrent duplicates
        new_event = PackerEventModel(
            event_id=payload.event_id,
            event_type=payload.event_type,
            order_id=payload.order_id,
            occurred_at=payload.occurred_at,
            received_at=datetime.now(timezone.utc),
            status="PROCESSED",
            payload=payload.model_dump(mode='json')
        )
        session.add(new_event)
        
        try:
            # Flush to enforce the unique constraint on event_id, protecting against concurrent duplicates
            await session.flush()
        except IntegrityError:
            # A concurrent request just inserted this event_id
            await session.rollback()
            return {"status": "ALREADY_PROCESSED"}

        # 5. Resolve SKUs and create movements
        for item in payload.items:
            stmt_sku = select(SKUModel).where(SKUModel.sku_code == item.sku)
            sku_res = await session.execute(stmt_sku)
            sku_obj = sku_res.scalars().first()
            if not sku_obj:
                raise ValidationException(f"SKU '{item.sku}' not found in SKU master.")

            mov_create = InventoryMovementCreate(
                movement_number=f"PACK-{payload.order_id}-{sku_obj.id}-{payload.event_id}",
                movement_type="SALES_FULFILLMENT",
                movement_date=payload.occurred_at.date(),
                posting_date=datetime.now(timezone.utc).date(),
                status="POSTED",
                warehouse_id=warehouse_id,
                sku_id=sku_obj.id,
                quantity=-item.quantity,  # Negative for SALES_FULFILLMENT
                reference_type="PACKER_ORDER",
                reference_number=payload.order_id,
                reference_id=payload.event_id # Use event_id as the authoritative reference
            )
            # Use an empty UUID for the system user creating this via webhook
            system_user_id = uuid.UUID(int=0)
            try:
                await self.movement_service.create_movement(mov_create, user_id=system_user_id, session=session)
            except IntegrityError:
                await session.rollback()
                return {"status": "ALREADY_PROCESSED"}

        return {"status": "PROCESSED"}
