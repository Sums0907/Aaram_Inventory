import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domains.connectors.models.report import DownloadedReportModel
from src.domains.connectors.services.base import MarketplaceConnector, DownloadedFileContext
from src.domains.connectors.services.storage import StorageManager
from src.domains.data_ingestion.services.import_job import ImportJobService

class SyncService:
    def __init__(
        self, 
        session: AsyncSession, 
        connector: MarketplaceConnector, 
        storage_manager: StorageManager,
        import_job_service: ImportJobService
    ):
        self.session = session
        self.connector = connector
        self.storage_manager = storage_manager
        self.import_job_service = import_job_service

    async def _is_duplicate(self, checksum: str) -> bool:
        stmt = select(DownloadedReportModel).where(DownloadedReportModel.checksum == checksum)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def run_sync(self, user_id: uuid.UUID, period_start: Optional[date] = None, period_end: Optional[date] = None, report_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Orchestrates the synchronization process.
        """
        sync_run_id = uuid.uuid4()
        
        # 1. Authenticate
        auth_success = await self.connector.authenticate()
        if not auth_success:
            return {"status": "FAILED", "reason": "Authentication failed", "sync_run_id": str(sync_run_id)}
            
        results = []
        
        try:
            async for file_ctx in self.connector.download_reports(period_start=period_start, period_end=period_end, report_type=report_type):
                checksum = self.storage_manager.generate_checksum(file_ctx.file_content)
                
                # Check for duplicates
                is_duplicate = await self._is_duplicate(checksum)
                
                if is_duplicate:
                    results.append({
                        "filename": file_ctx.filename,
                        "status": "DUPLICATE"
                    })
                    continue
                    
                # Save file
                storage_path = self.storage_manager.save_file(
                    marketplace_id=self.connector.marketplace_id,
                    filename=file_ctx.filename,
                    file_content=file_ctx.file_content
                )
                
                # Create Audit Record
                report_record = DownloadedReportModel(
                    source=self.connector.marketplace_id,
                    report_type=file_ctx.report_type,
                    period_start=file_ctx.period_start,
                    period_end=file_ctx.period_end,
                    downloaded_at=datetime.utcnow(),
                    checksum=checksum,
                    storage_path=storage_path,
                    status="DOWNLOADED",
                    sync_run_id=sync_run_id,
                    created_by=user_id,
                    updated_by=user_id
                )
                self.session.add(report_record)
                
                # Create Data Ingestion Job
                # We map connector terms to the exact codes required by the Data Ingestion pipeline
                from src.domains.data_ingestion.schemas.import_job import ImportJobCreate
                from src.domains.data_ingestion.schemas.import_file import ImportFileCreate
                
                integration_code = self.connector.marketplace_id
                
                # Find the integration_id based on integration_code
                from src.domains.data_ingestion.models.integration import IntegrationModel
                stmt = select(IntegrationModel).where(IntegrationModel.integration_code == integration_code)
                result = await self.session.execute(stmt)
                integration = result.scalars().first()
                integration_id = integration.id if integration else uuid.uuid4()
                
                # Map connector report_type to job_type
                job_type_map = {
                    "ORDER_RECONCILIATION": "SHOPDECK_ORDERS",
                    "TAX_READY": "SHOPDECK_TAX",
                    "COD_SETTLEMENT": "SHOPDECK_COD_SETTLEMENT",
                    "RAZORPAY_SETTLEMENT": "RAZORPAY_SETTLEMENT"
                }
                job_type = job_type_map.get(file_ctx.report_type, file_ctx.report_type)
    
                job_schema = ImportJobCreate(
                    integration_id=integration_id,
                    job_type=job_type,
                    status="PROCESSING" # Or PENDING, depending on if it's parsed later
                )
                import_job = await self.import_job_service.create_job(job_schema, user_id)
                
                # Create Import File record
                from src.domains.data_ingestion.services.import_file import ImportFileService
                from src.domains.data_ingestion.repositories.import_file import ImportFileRepository
                import hashlib
                
                file_service = ImportFileService(repository=ImportFileRepository(session=self.session))
                file_schema = ImportFileCreate(
                    import_job_id=import_job.id,
                    file_name=file_ctx.filename,
                    file_size_bytes=len(file_ctx.file_content),
                    mime_type="text/csv",
                    md5_hash=hashlib.md5(file_ctx.file_content).hexdigest()
                )
                await file_service.create_file_record(file_schema, user_id)
                
                # Synchronously parse using adapter (for Version 1)
                from src.domains.data_ingestion.services.adapters.shopdeck_order import ShopDeckOrderAdapter
                from src.domains.data_ingestion.services.adapters.shopdeck_tax import ShopDeckTaxAdapter
                from src.domains.data_ingestion.services.adapters.shopdeck_cod_settlement import ShopDeckCODSettlementAdapter
                from src.domains.data_ingestion.services.adapters.razorpay_settlement import RazorpaySettlementAdapter
                
                from src.domains.data_ingestion.repositories.import_record import ImportRecordRepository
                from src.domains.data_ingestion.repositories.import_error import ImportErrorRepository
                from src.domains.data_ingestion.repositories.import_summary import ImportSummaryRepository
                from src.domains.data_ingestion.services.import_record import ImportRecordService
                from src.domains.data_ingestion.services.import_error import ImportErrorService
                from src.domains.data_ingestion.services.import_summary import ImportSummaryService
                
                record_service = ImportRecordService(repository=ImportRecordRepository(session=self.session))
                error_service = ImportErrorService(repository=ImportErrorRepository(session=self.session))
                summary_service = ImportSummaryService(repository=ImportSummaryRepository(session=self.session))
                
                if job_type == "SHOPDECK_ORDERS":
                    adapter = ShopDeckOrderAdapter(record_service, error_service, summary_service)
                    await adapter.parse_and_ingest(file_ctx.file_content, import_job.id, user_id)
                elif job_type == "SHOPDECK_TAX":
                    adapter = ShopDeckTaxAdapter(record_service, error_service, summary_service)
                    await adapter.parse_and_ingest(file_ctx.file_content, import_job.id, user_id)
                elif job_type == "SHOPDECK_COD_SETTLEMENT":
                    adapter = ShopDeckCODSettlementAdapter(record_service, error_service, summary_service)
                    await adapter.parse_and_ingest(file_ctx.file_content, import_job.id, user_id)
                elif job_type == "RAZORPAY_SETTLEMENT":
                    adapter = RazorpaySettlementAdapter(record_service, error_service, summary_service)
                    await adapter.parse_and_ingest(file_ctx.file_content, import_job.id, user_id)
                    
                await self.import_job_service.update_job_status(import_job.id, "COMPLETED", user_id)
                
                report_record.status = "IMPORTED"
                
                results.append({
                    "filename": file_ctx.filename,
                    "status": "IMPORTED",
                    "import_job_id": str(import_job.id)
                })
                
        except Exception as e:
            return {
                "status": "FAILED",
                "reason": str(e),
                "sync_run_id": str(sync_run_id),
                "files_processed": results
            }
            
        await self.session.commit()
        
        return {
            "status": "SUCCESS",
            "sync_run_id": str(sync_run_id),
            "files_processed": results
        }
