from uuid import UUID
import uuid
from datetime import date
from typing import Optional
from sqlalchemy import select
from src.foundation.database.models import SequenceModel
from src.domains.inventory.repositories.job_work import JobWorkRepository
from src.domains.inventory.schemas.job_work import JobWorkIssueCreate, JobWorkReturnCreate
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.foundation.exceptions.base import ValidationException
from decimal import Decimal

async def get_next_sequence_value(session, sequence_name: str) -> int:
    # Use with_for_update for transaction-safe sequence generation
    stmt = select(SequenceModel).where(SequenceModel.sequence_name == sequence_name).with_for_update()
    res = await session.execute(stmt)
    seq = res.scalars().first()
    
    if not seq:
        seq = SequenceModel(sequence_name=sequence_name, last_value=1)
        session.add(seq)
        return 1
    
    seq.last_value += 1
    return seq.last_value

class JobWorkService:
    def __init__(
        self, 
        repository: JobWorkRepository,
        movement_service: InventoryMovementService
    ):
        self.repository = repository
        self.movement_service = movement_service

    async def issue_material(self, schema: JobWorkIssueCreate, created_by: UUID):
        session = self.repository.session
        
        today = date.today()
        # JW-ISS-DDMMYY
        seq_name = f"JW-ISS-{today.strftime('%d%m%y')}"
        seq_val = await get_next_sequence_value(session, seq_name)
        issue_reference = f"{seq_name}-{seq_val:03d}"
        
        warehouse_id = schema.warehouse_id
        if not warehouse_id:
            from src.domains.masters.models.warehouse import WarehouseModel
            stmt = select(WarehouseModel).limit(1)
            res = await self.repository.session.execute(stmt)
            warehouse = res.scalars().first()
            if not warehouse:
                raise ValidationException("No warehouse found to issue material from.")
            warehouse_id = warehouse.id

        # Validate sufficient stock in primary warehouse
        primary_stock = await self.movement_service.get_balance(warehouse_id, schema.item_id)
        if primary_stock < schema.quantity:
            raise ValidationException(f"Insufficient inventory. Available: {primary_stock}")

        try:
            issue = await self.repository.create_issue(issue_reference, schema, created_by)
            
            mov_create = InventoryMovementCreate(
                movement_number=f"MOV-JWI-{uuid.uuid4().hex[:8].upper()}",
                movement_type="JOB_WORK_ISSUE",
                movement_date=today,
                posting_date=today,
                status="POSTED",
                warehouse_id=warehouse_id,
                sku_id=schema.item_id,
                quantity=-abs(schema.quantity), # Deduct from main warehouse
                reference_type="JOB_WORK_ISSUE",
                reference_number=issue_reference,
                reference_id=schema.job_worker_id
            )
            await self.movement_service.create_movement(mov_create, created_by, session=session)
            await session.commit()
            return issue
        except Exception as e:
            await session.rollback()
            raise e

    async def return_material(self, schema: JobWorkReturnCreate, created_by: UUID):
        session = self.repository.session
        
        today = date.today()
        seq_name = f"JWR-{today.strftime('%d%m%y')}"
        seq_val = await get_next_sequence_value(session, seq_name)
        return_number = f"{seq_name}-{seq_val:03d}"
        
        warehouse_id = schema.warehouse_id
        if not warehouse_id:
            from src.domains.masters.models.warehouse import WarehouseModel
            stmt = select(WarehouseModel).limit(1)
            res = await self.repository.session.execute(stmt)
            warehouse = res.scalars().first()
            if not warehouse:
                raise ValidationException("No warehouse found to return material to.")
            warehouse_id = warehouse.id

        if schema.quantity <= 0:
            raise ValidationException("Returned quantity must be greater than 0.")

        try:
            # Create JOB_WORK_RETURN movement
            mov_create = InventoryMovementCreate(
                movement_number=f"MOV-JWR-{uuid.uuid4().hex[:8].upper()}",
                movement_type="JOB_WORK_RETURN",
                movement_date=today,
                posting_date=today,
                status="POSTED",
                warehouse_id=warehouse_id,
                sku_id=schema.item_id,
                quantity=schema.quantity, # Add back to main warehouse
                reference_type="JOB_WORK_RETURN",
                reference_number=return_number,
                reference_id=schema.job_worker_id
            )
            movement = await self.movement_service.create_movement(mov_create, created_by, session=session)
            
            # allocate return and update pending quantity correctly using FIFO
            await self.repository.allocate_return(
                schema.job_worker_id, 
                schema.item_id, 
                Decimal(str(schema.quantity)), 
                movement.id, 
                created_by
            )
            
            job_return = await self.repository.create_return(return_number, schema, created_by)
            
            await session.commit()
            return job_return
        except Exception as e:
            await session.rollback()
            raise e

    async def get_pending_stock(self, job_worker_id: UUID):
        return await self.repository.get_pending_stock(job_worker_id)

    async def get_all_pending_stock(self):
        return await self.repository.get_all_pending_stock()
        
    async def get_pending_stock_kpis(self):
        return await self.repository.get_pending_stock_kpis()

    async def get_custody_ledger(self, supplier_id: UUID, item_id: Optional[UUID] = None) -> dict:
        return await self.repository.get_stock_custody_ledger(supplier_id, item_id)

