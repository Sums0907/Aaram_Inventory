import csv
from uuid import UUID
from datetime import datetime
from typing import Dict, Any, List
from src.domains.data_ingestion.schemas.import_record import ImportRecordCreate
from src.domains.data_ingestion.schemas.import_error import ImportErrorCreate

class ShopDeckCODSettlementReader:
    def read(self, file_content: bytes) -> List[Dict[str, Any]]:
        content_str = file_content.decode('utf-8-sig')
        lines = content_str.splitlines()
        
        reader = csv.DictReader(lines)
        
        raw_rows = []
        row_number = 1
        
        for row in reader:
            row_number += 1
            if not row.get("Remittance ID") and not any(row.values()):
                continue
            
            raw_rows.append({
                "data": row,
                "row_number": row_number
            })
            
        return raw_rows

class ShopDeckCODSettlementValidator:
    def validate(self, raw_row: Dict[str, Any]) -> List[Dict[str, Any]]:
        errors = []
        if not raw_row["data"].get("Remittance ID"):
            errors.append({
                "error_code": "MISSING_REMITTANCE_ID",
                "error_message": "Row is missing Remittance ID",
                "row_number": raw_row["row_number"]
            })
        return errors

class ShopDeckCODSettlementMapper:
    def _parse_float(self, value: str) -> float:
        if not value or value.strip() == "":
            return 0.0
        try:
            return float(str(value).replace(',', '').strip())
        except ValueError:
            return 0.0
            
    def _parse_date(self, value: str) -> str:
        if not value or not str(value).strip():
            return ""
        try:
            # Format in CSV is "02 May 2026"
            parsed = datetime.strptime(str(value).strip(), "%d %b %Y")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            return str(value).strip()

    def map(self, raw_row: Dict[str, Any]) -> Dict[str, Any]:
        row = raw_row["data"]
        
        return {
            "settlement_id": row.get("Remittance ID", "").strip(),
            "cycle_date": row.get("Cycle Date", "").strip(),
            "settlement_date": self._parse_date(row.get("Payment Date", "")),
            "status": row.get("Settlement Status", "").strip(),
            "gross_amount": self._parse_float(row.get("Total COD Sales Amount", "")),
            "fees": self._parse_float(row.get("Total Expenses", "")),
            "net_amount": self._parse_float(row.get("Amount Transferred to Seller", "")),
            "utr_number": row.get("UTR", "").strip(),
            "bank_account": row.get("Bank Account No", "").strip()
        }

class ShopDeckCODSettlementAdapter:
    def __init__(self, record_service, error_service, summary_service):
        self.record_service = record_service
        self.error_service = error_service
        self.summary_service = summary_service
        self.reader = ShopDeckCODSettlementReader()
        self.validator = ShopDeckCODSettlementValidator()
        self.mapper = ShopDeckCODSettlementMapper()

    async def parse_and_ingest(self, file_content: bytes, job_id: UUID, created_by: UUID) -> None:
        raw_rows = self.reader.read(file_content)
        
        records_to_create = []
        errors_to_log = []
        
        for raw_row in raw_rows:
            validation_errors = self.validator.validate(raw_row)
            if validation_errors:
                for err in validation_errors:
                    errors_to_log.append(ImportErrorCreate(
                        import_job_id=job_id,
                        error_code=err["error_code"],
                        error_message=err["error_message"],
                        row_number=err.get("row_number")
                    ))
                continue
                
            normalized = self.mapper.map(raw_row)
            
            records_to_create.append(
                ImportRecordCreate(
                    import_job_id=job_id,
                    record_type="SETTLEMENT",
                    raw_data={"row": raw_row["data"]},
                    status="VALID",
                    normalized_data=normalized
                )
            )

        if records_to_create:
            batch_size = 500
            for i in range(0, len(records_to_create), batch_size):
                await self.record_service.create_records_batch(records_to_create[i:i + batch_size], created_by)

        if errors_to_log:
            await self.error_service.log_errors_batch(errors_to_log, created_by)

        await self.summary_service.generate_initial_summary(job_id=job_id, total_records=len(raw_rows), created_by=created_by)
        await self.summary_service.update_summary_stats(
            job_id=job_id,
            successful=len(records_to_create),
            failed=len(raw_rows) - len(records_to_create),
            duplicate=0,
            updated_by=created_by
        )
