from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime



class JobWorkIssueBase(BaseModel):
    job_worker_id: UUID
    item_id: UUID
    quantity: float = Field(..., gt=0)

class JobWorkIssueCreate(JobWorkIssueBase):
    warehouse_id: Optional[UUID] = None

class JobWorkIssueResponse(BaseModel):
    id: UUID
    issue_reference: str
    job_worker_id: UUID
    item_id: UUID
    issued_quantity: float
    consumed_quantity: float
    returned_quantity: float
    pending_quantity: float
    created_on: datetime
    updated_on: datetime

class JobWorkReturnBase(BaseModel):
    job_worker_id: UUID
    item_id: UUID
    quantity: float = Field(..., gt=0)

class JobWorkReturnCreate(JobWorkReturnBase):
    warehouse_id: Optional[UUID] = None

class JobWorkReturnResponse(JobWorkReturnBase):
    id: UUID
    return_number: str
    created_on: datetime
    updated_on: datetime

class JobWorkReceiptBase(BaseModel):
    job_worker_id: UUID
    item_id: UUID
    quantity: float = Field(..., gt=0)
    scrap_quantity: float = 0

class JobWorkReceiptCreate(JobWorkReceiptBase):
    pass

class JobWorkReceiptResponse(JobWorkReceiptBase):
    id: UUID
    receipt_number: str
    created_on: datetime
    updated_on: datetime

class JobWorkerInventoryResponse(BaseModel):
    job_worker_id: UUID
    item_id: UUID
    issued_quantity: float
    consumed_quantity: float
    returned_quantity: float
    pending_quantity: float
    last_movement_id: Optional[UUID]

class InventoryTransformationRecordResponse(BaseModel):
    id: UUID
    source_item_id: UUID
    destination_item_id: UUID
    quantity_consumed: float
    quantity_produced: float
    source_uom_id: Optional[UUID]
    destination_uom_id: Optional[UUID]
    bom_id: Optional[UUID]
    bom_quantity_per_unit: Optional[float]
    job_worker_id: Optional[UUID]
    reference_document: str
    transformation_reason: str
    created_on: datetime

class JobWorkerInventoryDetailResponse(JobWorkerInventoryResponse):
    job_worker_name: str
    item_code: str
    item_name: str
    uom: str
    issues: List[JobWorkIssueResponse] = []

class JobWorkerStockKPIResponse(BaseModel):
    job_workers_with_stock: int
    items_with_pending_stock: int
    total_pending_lines: int

class JobWorkerPendingStockResponse(BaseModel):
    kpis: JobWorkerStockKPIResponse
    items: List[JobWorkerInventoryDetailResponse]

class StockCustodyLedgerEntry(BaseModel):
    date: str
    reference: str
    particular: str
    issue: str
    consumption: str
    return_qty: str = Field(..., alias="return")
    pending: str

    class Config:
        populate_by_name = True

class StockCustodyLedgerItemSummary(BaseModel):
    item_id: str
    item_code: str
    item_name: str
    uom: str
    entries: List[StockCustodyLedgerEntry]

class StockCustodyLedgerResponse(BaseModel):
    supplier_id: str
    supplier_name: str
    items: List[StockCustodyLedgerItemSummary]

