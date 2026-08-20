import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.domains.data_ingestion.models.import_audit_log import ImportAuditLogModel
from src.domains.data_ingestion.services.master_data_importer import ImportResult
from src.domains.data_ingestion.services.uom_importer import UOMImporter
from src.domains.data_ingestion.services.category_importer import CategoryImporter
from src.domains.data_ingestion.services.supplier_importer import SupplierImporter
from src.domains.data_ingestion.services.product_sku_importer import ProductSKUImporter
from src.domains.data_ingestion.services.bom_importer import BOMImporter
from src.domains.data_ingestion.services.master_data_exporter import MasterDataExporter

IMPORTERS = {
    "UOM":                  UOMImporter,
    "OPERATIONAL_CATEGORY": CategoryImporter,
    "SUPPLIER":             SupplierImporter,
    "RAW_MATERIAL":         ProductSKUImporter,
    "BOM":                  BOMImporter,
    "CATEGORY":             CategoryImporter,
    "PRODUCT_SKU":          ProductSKUImporter,
}

class MasterDataApplicationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def validate_permissions(self, user_permissions: List[str], required_permissions: List[str]):
        """
        Validates if the user has any of the required permissions.
        """
        if not any(permission in user_permissions for permission in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation."
            )

    async def execute_import(
        self,
        domain: str,
        data: List[Dict[str, Any]],
        is_dry_run: bool,
        user_id: Optional[str] = None,
        file_name: str = "api_upload.xlsx",
        env: str = "prod"
    ) -> Dict[str, Any]:
        """
        Executes an import job for a given domain, handling audit logging and session commit/rollback.
        """
        domain_upper = domain.upper()
        if domain_upper not in IMPORTERS:
            raise ValueError(f"Unknown import domain '{domain}'. Allowed domains: {list(IMPORTERS.keys())}")

        importer_class = IMPORTERS[domain_upper]
        importer = importer_class(self.session)
        
        batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"
        start_time = datetime.datetime.utcnow()
        status_label = "DRY_RUN" if is_dry_run else "COMMITTED"

        try:
            # 1. Run the import engine
            result = await importer.import_data(data, is_dry_run=is_dry_run)
            
            # 2. Add Audit Log
            audit_log = ImportAuditLogModel(
                id=uuid.uuid4(),
                batch_id=batch_id,
                filename=file_name,
                entity_type=domain_upper,
                environment=env,
                executed_by_user_id=uuid.UUID(user_id) if user_id else None,
                status=status_label,
                rollback_status="SUCCESS" if not is_dry_run else "NONE",
                records_processed=result.total_records,
                success_count=result.created_count + result.updated_count + result.ignored_count,
                failure_count=result.failed_count + result.ambiguous_count,
                start_time=start_time,
                end_time=datetime.datetime.utcnow()
            )
            self.session.add(audit_log)
            
            # 3. Transaction control
            if not is_dry_run:
                if result.failed_count > 0 or result.ambiguous_count > 0:
                    await self.session.rollback()
                    raise ValueError("Commit blocked: FAILED or AMBIGUOUS records > 0")
                await self.session.commit()
            else:
                await self.session.flush() # ensure audit log is pushed to allow potential read inside the transaction?
                # For dry_run, we still want to rollback but maybe we don't rollback until after? 
                # Wait, if we rollback, we lose the audit log. The CLI commits the audit log? No, CLI calls rollback.
                # If we want the audit log for dry-runs, we might need a separate transaction for the audit log.
                # I'll follow the exact CLI pattern:
                await self.session.rollback()
                
            return {
                "batch_id": batch_id,
                "entity_type": result.entity_type,
                "total_records": result.total_records,
                "created_count": result.created_count,
                "updated_count": result.updated_count,
                "ignored_count": result.ignored_count,
                "failed_count": result.failed_count,
                "ambiguous_count": result.ambiguous_count,
                "row_results": [
                    {
                        "row_index": r.row_index,
                        "action": r.action.value,
                        "entity_id": r.entity_id,
                        "identifier": r.identifier,
                        "errors": r.errors
                    } for r in result.row_results
                ],
                "global_errors": result.global_errors
            }
            
        except Exception as e:
            await self.session.rollback()
            raise e

    async def execute_export(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Executes a full export.
        """
        exporter = MasterDataExporter(self.session)
        return await exporter.export_all()

