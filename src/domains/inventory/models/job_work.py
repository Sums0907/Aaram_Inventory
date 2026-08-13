from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, Numeric
from src.foundation.database.models import BaseModel


class JobWorkIssueModel(BaseModel):
    __tablename__ = "inventory_job_work_issues"

    issue_reference: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    job_worker_id: Mapped[UUID] = mapped_column(ForeignKey("masters_suppliers.id"), nullable=False, index=True)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    issued_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    consumed_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False, default=0)
    returned_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False, default=0)
    pending_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)

class JobWorkAllocationModel(BaseModel):
    __tablename__ = "inventory_job_work_allocations"

    issue_id: Mapped[UUID] = mapped_column(ForeignKey("inventory_job_work_issues.id"), nullable=False, index=True)
    movement_id: Mapped[UUID] = mapped_column(ForeignKey("inventory_movements.id"), nullable=False, index=True)
    allocation_type: Mapped[str] = mapped_column(String(50), nullable=False) # CONSUMPTION, RETURN
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)


class JobWorkReturnModel(BaseModel):
    __tablename__ = "inventory_job_work_returns"

    return_number: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    job_worker_id: Mapped[UUID] = mapped_column(ForeignKey("masters_suppliers.id"), nullable=False, index=True)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)


class JobWorkReceiptModel(BaseModel):
    __tablename__ = "inventory_job_work_receipts"

    receipt_number: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    job_worker_id: Mapped[UUID] = mapped_column(ForeignKey("masters_suppliers.id"), nullable=False, index=True)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    scrap_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False, default=0)


class JobWorkerInventoryModel(BaseModel):
    __tablename__ = "inventory_job_worker_stock"

    job_worker_id: Mapped[UUID] = mapped_column(ForeignKey("masters_suppliers.id"), nullable=False, index=True)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    
    issued_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False, default=0)
    consumed_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False, default=0)
    returned_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False, default=0)
    pending_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False, default=0)
    
    last_movement_id: Mapped[UUID] = mapped_column(ForeignKey("inventory_movements.id"), nullable=True)


class InventoryTransformationRecord(BaseModel):
    __tablename__ = "inventory_transformation_register"

    source_item_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    destination_item_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    
    quantity_consumed: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    quantity_produced: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    
    source_uom_id: Mapped[UUID] = mapped_column(ForeignKey("units_of_measure.id"), nullable=True, index=True)
    destination_uom_id: Mapped[UUID] = mapped_column(ForeignKey("units_of_measure.id"), nullable=True, index=True)
    bom_id: Mapped[UUID] = mapped_column(ForeignKey("masters_boms.id"), nullable=True, index=True)
    bom_quantity_per_unit: Mapped[float] = mapped_column(Numeric(10, 4), nullable=True)
    
    job_worker_id: Mapped[UUID] = mapped_column(ForeignKey("masters_suppliers.id"), nullable=True, index=True)
    reference_document: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    transformation_reason: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
