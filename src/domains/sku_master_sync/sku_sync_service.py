from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import hashlib

from src.domains.sku_master_sync.shopdeck_reader import ShopDeckReader
from src.domains.sku_master_sync.sku_matcher import SkuMatcher
from src.domains.sku_master_sync.sku_diff_engine import SkuDiffEngine
from src.domains.sku_master_sync.finished_goods_category_sync import FinishedGoodsCategorySync
from src.domains.sku_master_sync.sku_creator import SkuCreator
from src.domains.sku_master_sync.sku_updater import SkuUpdater
from src.domains.sku_master_sync.sku_archiver import SkuArchiver
from src.domains.data_ingestion.models.import_audit_log import ImportAuditLogModel

class SkuSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.matcher = SkuMatcher(db)
        self.diff_engine = SkuDiffEngine()
        self.category_sync = FinishedGoodsCategorySync(db)
        self.creator = SkuCreator(db)
        self.updater = SkuUpdater(db)
        self.archiver = SkuArchiver(db)
        
    async def sync_catalogue(self, csv_content: str, filename: str, run_mode: str = "DRY_RUN", user_id: Optional[uuid.UUID] = None) -> str:
        """
        Orchestrates the SKU Master Sync process.
        Returns a formatted report string.
        """
        start_time = datetime.utcnow()
        batch_id = str(uuid.uuid4())
        file_hash = hashlib.sha256(csv_content.encode("utf-8")).hexdigest()
        
        # 1. Parse CSV
        try:
            parsed_rows = ShopDeckReader.parse_csv(csv_content)
        except Exception as e:
            await self._log_audit(batch_id, filename, "FAILED", 0, 0, 0, start_time, user_id)
            return f"SHOPDECK SKU CATALOGUE SYNC REPORT\n\nFailed to parse CSV: {str(e)}"
            
        # 2. Match Identities
        new_rows, existing_rows, missing_skus, errors = await self.matcher.match(parsed_rows)
        
        if errors:
            await self._log_audit(batch_id, filename, "FAILED", len(parsed_rows), 0, len(errors), start_time, user_id)
            return self.diff_engine.format_report([], [], [], [], errors)
            
        # 3. Diff Engine
        updated_rows, ignored_rows = self.diff_engine.calculate_diffs(existing_rows)
        
        # Calculate final counts
        created_count = len(new_rows)
        updated_count = len(updated_rows)
        archived_count = len(missing_skus)
        ignored_count = len(ignored_rows)
        
        # Format Report
        report = self.diff_engine.format_report(new_rows, updated_rows, missing_skus, ignored_rows, [])
        
        # 4. Commit Engine if not DRY_RUN
        if run_mode == "COMMITTED":
            try:
                # Process Creates
                for row in new_rows:
                    category = await self.category_sync.resolve(row["category_path"])
                    await self.creator.create(row, category)
                    
                # Process Updates
                for u in updated_rows:
                    category = await self.category_sync.resolve(u["csv_row"]["category_path"])
                    await self.updater.update(u["db_sku"], u["csv_row"], category)
                    
                # Process Archives
                for sku in missing_skus:
                    await self.archiver.archive(sku)
                    
                await self.db.commit()
                status = "COMMITTED"
            except Exception as e:
                await self.db.rollback()
                await self._log_audit(batch_id, filename, "FAILED", len(parsed_rows), 0, len(parsed_rows), start_time, user_id)
                raise e
        else:
            status = "DRY_RUN"
            
        # 5. Log Audit
        success_count = created_count + updated_count + archived_count + ignored_count
        await self._log_audit(batch_id, filename, status, len(parsed_rows), success_count, 0, start_time, user_id)
        
        return report

    async def _log_audit(self, batch_id: str, filename: str, status: str, total: int, success: int, failed: int, start_time: datetime, user_id: Optional[uuid.UUID]):
        # Just create the log and commit it separately
        audit = ImportAuditLogModel(
            batch_id=batch_id,
            filename=filename,
            entity_type="SHOPDECK_SKU_CATALOGUE_SYNC",
            environment="PRODUCTION",
            executed_by_user_id=user_id,
            status=status,
            records_processed=total,
            success_count=success,
            failure_count=failed,
            start_time=start_time,
            end_time=datetime.utcnow()
        )
        self.db.add(audit)
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
