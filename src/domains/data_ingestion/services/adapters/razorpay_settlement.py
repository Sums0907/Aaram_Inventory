import csv
from uuid import UUID
from datetime import datetime
from typing import Dict, Any, List
from src.domains.data_ingestion.schemas.import_record import ImportRecordCreate
from src.domains.data_ingestion.schemas.import_error import ImportErrorCreate

class RazorpaySettlementReader:
    def read(self, file_content: bytes) -> List[Dict[str, Any]]:
        content_str = file_content.decode('utf-8-sig')
        lines = content_str.splitlines()
        
        reader = csv.DictReader(lines)
        
        raw_rows = []
        row_number = 1
        
        for row in reader:
            row_number += 1
            if not row.get("entity_id") and not any(row.values()):
                continue
            
            raw_rows.append({
                "data": row,
                "row_number": row_number
            })
            
        return raw_rows

class RazorpaySettlementValidator:
    def validate(self, raw_row: Dict[str, Any]) -> List[Dict[str, Any]]:
        errors = []
        if not raw_row["data"].get("entity_id"):
            errors.append({
                "error_code": "MISSING_ENTITY_ID",
                "error_message": "Row is missing entity_id",
                "row_number": raw_row["row_number"]
            })
        return errors

class RazorpaySettlementMapper:
    def _parse_float(self, value: str) -> float:
        if not value or value.strip() == "":
            return 0.0
        try:
            return float(str(value).replace(',', '').strip())
        except ValueError:
            return 0.0
            
    def _parse_datetime(self, value: str) -> str:
        if not value or not str(value).strip():
            return ""
        try:
            # Format in CSV is "30/03/2026 12:07:30"
            parsed = datetime.strptime(str(value).strip(), "%d/%m/%Y %H:%M:%S")
            return parsed.isoformat()
        except ValueError:
            return str(value).strip()

    def map(self, raw_row: Dict[str, Any]) -> Dict[str, Any]:
        row = raw_row["data"]
        
        return {
            "transaction_id": row.get("entity_id", "").strip(),
            "transaction_type": row.get("transaction_entity", "").strip(),
            "order_reference": row.get("order_receipt", "").strip(), # This is UNMATCHED right now as per user instruction
            "external_settlement_id": row.get("settlement_id", "").strip(),
            "payment_method": row.get("payment_method", "").strip(),
            "gross_amount": self._parse_float(row.get("amount", "")),
            "gateway_fee": self._parse_float(row.get("fee (exclusive tax)", "")) + self._parse_float(row.get("tax", "")),
            "net_amount": self._parse_float(row.get("credit", "")),
            "payment_captured_at": self._parse_datetime(row.get("payment_captured_at", "")),
            "utr_number": row.get("settlement_utr", "").strip()
        }

class RazorpaySettlementAdapter:
    def __init__(self, record_service, error_service, summary_service):
        self.record_service = record_service
        self.error_service = error_service
        self.summary_service = summary_service
        self.reader = RazorpaySettlementReader()
        self.validator = RazorpaySettlementValidator()
        self.mapper = RazorpaySettlementMapper()

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
                    record_type="PAYMENT",
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
