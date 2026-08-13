from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.inventory.models.job_work import JobWorkIssueModel, JobWorkReceiptModel, JobWorkerInventoryModel, InventoryTransformationRecord, JobWorkReturnModel, JobWorkAllocationModel
from src.domains.inventory.schemas.job_work import JobWorkIssueCreate, JobWorkReceiptCreate, JobWorkReturnCreate
from decimal import Decimal
from src.foundation.exceptions.base import ValidationException

class JobWorkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_total_pending_stock_kpi(self) -> int:
        from sqlalchemy import func
        stmt = select(func.count(JobWorkerInventoryModel.id)).where(JobWorkerInventoryModel.pending_quantity > 0)
        res = await self.session.execute(stmt)
        return res.scalar() or 0

    async def create_issue(self, issue_reference: str, schema: JobWorkIssueCreate, created_by: UUID) -> JobWorkIssueModel:
        db_obj = JobWorkIssueModel(
            issue_reference=issue_reference,
            job_worker_id=schema.job_worker_id,
            item_id=schema.item_id,
            issued_quantity=schema.quantity,
            consumed_quantity=0,
            returned_quantity=0,
            pending_quantity=schema.quantity,
            created_by=created_by,
            updated_by=created_by
        )
        self.session.add(db_obj)
        
        # Update or create JobWorkerInventoryModel
        stmt = select(JobWorkerInventoryModel).where(
            JobWorkerInventoryModel.job_worker_id == schema.job_worker_id,
            JobWorkerInventoryModel.item_id == schema.item_id
        )
        res = await self.session.execute(stmt)
        stock = res.scalars().first()
        if not stock:
            stock = JobWorkerInventoryModel(
                job_worker_id=schema.job_worker_id,
                item_id=schema.item_id,
                issued_quantity=0,
                consumed_quantity=0,
                returned_quantity=0,
                pending_quantity=0,
                created_by=created_by,
                updated_by=created_by
            )
            self.session.add(stock)
        
        stock.issued_quantity = Decimal(str(stock.issued_quantity)) + Decimal(str(schema.quantity))
        stock.pending_quantity = Decimal(str(stock.pending_quantity)) + Decimal(str(schema.quantity))

        return db_obj

    async def create_return(self, return_number: str, schema: JobWorkReturnCreate, created_by: UUID) -> JobWorkReturnModel:
        db_obj = JobWorkReturnModel(
            return_number=return_number,
            job_worker_id=schema.job_worker_id,
            item_id=schema.item_id,
            quantity=schema.quantity,
            created_by=created_by,
            updated_by=created_by
        )
        self.session.add(db_obj)
        return db_obj

    async def allocate_consumption(self, job_worker_id: UUID, item_id: UUID, required_qty: Decimal, movement_id: UUID, created_by: UUID):
        stmt = select(JobWorkIssueModel).where(
            JobWorkIssueModel.job_worker_id == job_worker_id,
            JobWorkIssueModel.item_id == item_id,
            JobWorkIssueModel.pending_quantity > 0
        ).order_by(JobWorkIssueModel.created_on.asc())
        
        res = await self.session.execute(stmt)
        issues = res.scalars().all()
        
        remaining_qty_to_allocate = required_qty
        
        for issue in issues:
            if remaining_qty_to_allocate <= Decimal("0"):
                break
                
            issue_pending = Decimal(str(issue.pending_quantity))
            allocate_qty = min(issue_pending, remaining_qty_to_allocate)
            
            # Update issue
            issue.consumed_quantity = Decimal(str(issue.consumed_quantity)) + allocate_qty
            issue.pending_quantity = issue_pending - allocate_qty
            
            # Create allocation record
            allocation = JobWorkAllocationModel(
                issue_id=issue.id,
                movement_id=movement_id,
                allocation_type="CONSUMPTION",
                quantity=allocate_qty,
                created_by=created_by,
                updated_by=created_by
            )
            self.session.add(allocation)
            
            remaining_qty_to_allocate -= allocate_qty
            
        if remaining_qty_to_allocate > Decimal("0"):
            raise ValidationException(f"Insufficient pending issues to allocate consumption. Shortfall: {remaining_qty_to_allocate}")

    async def allocate_return(self, job_worker_id: UUID, item_id: UUID, return_qty: Decimal, movement_id: UUID, created_by: UUID):
        stmt = select(JobWorkIssueModel).where(
            JobWorkIssueModel.job_worker_id == job_worker_id,
            JobWorkIssueModel.item_id == item_id,
            JobWorkIssueModel.pending_quantity > 0
        ).order_by(JobWorkIssueModel.created_on.asc())
        
        res = await self.session.execute(stmt)
        issues = res.scalars().all()
        
        remaining_qty_to_return = return_qty
        
        for issue in issues:
            if remaining_qty_to_return <= Decimal("0"):
                break
                
            issue_pending = Decimal(str(issue.pending_quantity))
            allocate_qty = min(issue_pending, remaining_qty_to_return)
            
            # Update issue
            issue.returned_quantity = Decimal(str(issue.returned_quantity)) + allocate_qty
            issue.pending_quantity = issue_pending - allocate_qty
            
            # Create allocation record
            allocation = JobWorkAllocationModel(
                issue_id=issue.id,
                movement_id=movement_id,
                allocation_type="RETURN",
                quantity=allocate_qty,
                created_by=created_by,
                updated_by=created_by
            )
            self.session.add(allocation)
            
            remaining_qty_to_return -= allocate_qty
            
        if remaining_qty_to_return > Decimal("0"):
            raise ValidationException(f"Cannot return more than pending stock. Shortfall: {remaining_qty_to_return}")
            
        # Update JobWorkerInventoryModel
        stmt = select(JobWorkerInventoryModel).where(
            JobWorkerInventoryModel.job_worker_id == job_worker_id,
            JobWorkerInventoryModel.item_id == item_id
        )
        res = await self.session.execute(stmt)
        stock = res.scalars().first()
        if not stock or stock.pending_quantity < return_qty:
            raise ValidationException("Returned quantity cannot exceed current pending quantity on summary.")
            
        stock.returned_quantity = Decimal(str(stock.returned_quantity)) + return_qty
        stock.pending_quantity = Decimal(str(stock.pending_quantity)) - return_qty


    async def get_pending_stock(self, job_worker_id: UUID) -> List[JobWorkerInventoryModel]:
        stmt = select(JobWorkerInventoryModel).where(JobWorkerInventoryModel.job_worker_id == job_worker_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_pending_stock_summary(self) -> List[dict]:
        from src.domains.masters.models.supplier import Supplier
        from sqlalchemy import func
        
        stmt = (
            select(
                JobWorkerInventoryModel.item_id,
                JobWorkerInventoryModel.job_worker_id,
                Supplier.name.label("job_worker_name"),
                func.sum(JobWorkerInventoryModel.pending_quantity).label("pending_quantity")
            )
            .join(Supplier, Supplier.id == JobWorkerInventoryModel.job_worker_id)
            .where(JobWorkerInventoryModel.pending_quantity > 0)
            .group_by(
                JobWorkerInventoryModel.item_id,
                JobWorkerInventoryModel.job_worker_id,
                Supplier.name
            )
        )
        res = await self.session.execute(stmt)
        return [dict(row._mapping) for row in res.fetchall()]

    async def get_all_pending_stock(self) -> List[dict]:
        from src.domains.masters.models.supplier import Supplier
        from src.domains.masters.models.sku import SKUModel
        from src.domains.masters.models.product import ProductModel
        from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
        
        stmt = (
            select(
                JobWorkerInventoryModel.job_worker_id,
                Supplier.name.label("job_worker_name"),
                JobWorkerInventoryModel.item_id,
                SKUModel.sku_code.label("item_code"),
                ProductModel.product_name.label("item_name"),
                UnitOfMeasureModel.short_name.label("uom"),
                JobWorkerInventoryModel.issued_quantity,
                JobWorkerInventoryModel.consumed_quantity,
                JobWorkerInventoryModel.returned_quantity,
                JobWorkerInventoryModel.pending_quantity,
                JobWorkerInventoryModel.last_movement_id
            )
            .join(Supplier, Supplier.id == JobWorkerInventoryModel.job_worker_id)
            .join(SKUModel, SKUModel.id == JobWorkerInventoryModel.item_id)
            .join(ProductModel, ProductModel.id == SKUModel.product_id)
            .join(UnitOfMeasureModel, UnitOfMeasureModel.id == SKUModel.uom_id)
            .where(JobWorkerInventoryModel.pending_quantity > 0)
        )
        res = await self.session.execute(stmt)
        results = [dict(row._mapping) for row in res.fetchall()]
        
        # Attach issues
        if results:
            stmt_issues = select(JobWorkIssueModel).where(JobWorkIssueModel.pending_quantity > 0)
            res_issues = await self.session.execute(stmt_issues)
            all_issues = res_issues.scalars().all()
            
            for row in results:
                row["issues"] = [
                    {
                        "id": str(i.id),
                        "issue_reference": i.issue_reference,
                        "job_worker_id": str(i.job_worker_id),
                        "item_id": str(i.item_id),
                        "issued_quantity": float(i.issued_quantity),
                        "consumed_quantity": float(i.consumed_quantity),
                        "returned_quantity": float(i.returned_quantity),
                        "pending_quantity": float(i.pending_quantity),
                        "created_on": i.created_on,
                        "updated_on": i.updated_on
                    }
                    for i in all_issues
                    if i.job_worker_id == row["job_worker_id"] and i.item_id == row["item_id"]
                ]
        
        return results

    async def get_pending_stock_kpis(self) -> dict:
        from sqlalchemy import func
        # 1. Job Workers with Stock
        stmt_workers = select(func.count(func.distinct(JobWorkerInventoryModel.job_worker_id))).where(JobWorkerInventoryModel.pending_quantity > 0)
        res_workers = await self.session.execute(stmt_workers)
        job_workers_with_stock = res_workers.scalar() or 0

        # 2. Items with Pending Stock
        stmt_items = select(func.count(func.distinct(JobWorkerInventoryModel.item_id))).where(JobWorkerInventoryModel.pending_quantity > 0)
        res_items = await self.session.execute(stmt_items)
        items_with_pending_stock = res_items.scalar() or 0

        # 3. Total Pending Lines
        stmt_lines = select(func.count(JobWorkerInventoryModel.id)).where(JobWorkerInventoryModel.pending_quantity > 0)
        res_lines = await self.session.execute(stmt_lines)
        total_pending_lines = res_lines.scalar() or 0

        return {
            "job_workers_with_stock": job_workers_with_stock,
            "items_with_pending_stock": items_with_pending_stock,
            "total_pending_lines": total_pending_lines
        }

    async def get_stock_custody_ledger(self, supplier_id: UUID, item_id: Optional[UUID] = None) -> dict:
        from src.domains.masters.models.supplier import Supplier
        from src.domains.masters.models.sku import SKUModel
        from src.domains.masters.models.product import ProductModel
        from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
        from src.domains.inventory.models.movement import InventoryMovementModel
        from decimal import Decimal
        from collections import defaultdict
        
        # 1. Fetch supplier
        stmt_supplier = select(Supplier).where(Supplier.id == supplier_id)
        res_supp = await self.session.execute(stmt_supplier)
        supplier = res_supp.scalars().first()
        if not supplier:
            raise ValidationException("Job worker not found")
            
        # 2. Fetch movements
        stmt = (
            select(
                InventoryMovementModel,
                SKUModel.sku_code.label("item_code"),
                ProductModel.product_name.label("item_name"),
                UnitOfMeasureModel.short_name.label("uom")
            )
            .join(SKUModel, SKUModel.id == InventoryMovementModel.sku_id)
            .join(ProductModel, ProductModel.id == SKUModel.product_id)
            .join(UnitOfMeasureModel, UnitOfMeasureModel.id == SKUModel.uom_id)
            .where(
                InventoryMovementModel.reference_id == supplier_id,
                InventoryMovementModel.movement_type.in_([
                    "JOB_WORK_ISSUE",
                    "RAW_MATERIAL_CONSUMPTION",
                    "JOB_WORK_RETURN"
                ])
            )
            .order_by(InventoryMovementModel.created_on.asc())
        )
        
        if item_id:
            stmt = stmt.where(InventoryMovementModel.sku_id == item_id)
            
        res = await self.session.execute(stmt)
        rows = res.all()
        
        # 3. Group by item_id
        items_dict = defaultdict(lambda: {
            "item_id": "",
            "item_code": "",
            "item_name": "",
            "uom": "",
            "entries": [],
            "running_pending": Decimal("0")
        })
        
        for row in rows:
            mov = row[0]
            sku_id_str = str(mov.sku_id)
            
            if not items_dict[sku_id_str]["item_id"]:
                items_dict[sku_id_str]["item_id"] = sku_id_str
                items_dict[sku_id_str]["item_code"] = row.item_code
                items_dict[sku_id_str]["item_name"] = row.item_name
                items_dict[sku_id_str]["uom"] = row.uom
                
            qty = Decimal(str(mov.quantity))
            issue_val = Decimal("0")
            cons_val = Decimal("0")
            ret_val = Decimal("0")
            
            if mov.movement_type == "JOB_WORK_ISSUE":
                # Movement quantity is negative in warehouse, but it means issue to JW.
                issue_val = abs(qty)
                particular = "Material Issued"
            elif mov.movement_type == "RAW_MATERIAL_CONSUMPTION":
                # Movement quantity is negative in warehouse, and it means consumption.
                cons_val = abs(qty)
                particular = "Material Consumed"
            elif mov.movement_type == "JOB_WORK_RETURN":
                # Movement quantity is positive in warehouse, means return.
                ret_val = abs(qty)
                particular = "Material Returned"
                
            items_dict[sku_id_str]["running_pending"] += issue_val - cons_val - ret_val
            
            date_str = mov.created_on.strftime("%Y-%m-%d") if mov.created_on else mov.movement_date.strftime("%Y-%m-%d")
            
            items_dict[sku_id_str]["entries"].append({
                "date": date_str,
                "reference": mov.reference_number,
                "particular": particular,
                "issue": f"{issue_val:.2f}" if issue_val > 0 else "—",
                "consumption": f"{cons_val:.2f}" if cons_val > 0 else "—",
                "return": f"{ret_val:.2f}" if ret_val > 0 else "—",
                "pending": f"{items_dict[sku_id_str]['running_pending']:.2f}"
            })
            
        result_items = []
        for sku_id, data in items_dict.items():
            result_items.append({
                "item_id": data["item_id"],
                "item_code": data["item_code"],
                "item_name": data["item_name"],
                "uom": data["uom"],
                "entries": data["entries"]
            })
            
        return {
            "supplier_id": str(supplier_id),
            "supplier_name": supplier.name,
            "items": result_items
        }

