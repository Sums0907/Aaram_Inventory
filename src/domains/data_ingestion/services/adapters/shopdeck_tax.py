import csv
from uuid import UUID
from typing import Dict, Any, List
from src.domains.data_ingestion.schemas.import_record import ImportRecordCreate
from src.domains.data_ingestion.schemas.import_error import ImportErrorCreate

class ShopDeckTaxReader:
    def read(self, file_content: bytes) -> List[Dict[str, Any]]:
        content_str = file_content.decode('utf-8-sig')
        lines = content_str.splitlines()
        
        reader = csv.DictReader(lines)
        
        grouped_invoices: Dict[str, Dict[str, Any]] = {}
        row_number = 1 # Assuming header is line 1
        
        for row in reader:
            row_number += 1
            invoice_no = row.get("Invoice/CN No.", "").strip()
            
            if not invoice_no and not any(row.values()):
                continue
                
            if invoice_no not in grouped_invoices:
                grouped_invoices[invoice_no] = {
                    "invoice_no": invoice_no,
                    "rows": [],
                    "first_row_number": row_number
                }
            
            grouped_invoices[invoice_no]["rows"].append({
                "data": row,
                "row_number": row_number
            })
            
        return list(grouped_invoices.values())

class ShopDeckTaxValidator:
    def validate(self, grouped_raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        errors = []
        if not grouped_raw.get("invoice_no"):
            errors.append({
                "error_code": "MISSING_INVOICE_NO",
                "error_message": "Row is missing Invoice/CN No.",
                "row_number": grouped_raw.get("first_row_number")
            })
        return errors

class ShopDeckTaxMapper:
    def _parse_float(self, value: str) -> float:
        if not value or value.strip() in ("", "-"):
            return 0.0
        try:
            return float(str(value).replace(',', '').strip())
        except ValueError:
            return 0.0

    def _parse_date(self, value: str) -> str:
        if not value or not str(value).strip():
            return ""
        try:
            from datetime import datetime
            parsed = datetime.strptime(str(value).strip(), "%d-%m-%Y")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            return str(value).strip()

    def map(self, grouped_raw: Dict[str, Any]) -> Dict[str, Any]:
        rows = grouped_raw["rows"]
        first_row = rows[0]["data"]
        
        normalized = {
            "invoice_no": grouped_raw["invoice_no"],
            "external_order_id": first_row.get("Order ID", "").strip(),
            "document_type": first_row.get("Document Type", "").strip(),
            "invoice_date": self._parse_date(first_row.get("Document Creation Date", "")),
            "customer_state": first_row.get("Customer State", "").strip(),
            "total_base_price": 0.0,
            "total_tax": 0.0,
            "total_igst": 0.0,
            "total_cgst": 0.0,
            "total_sgst": 0.0,
            "items": []
        }
        
        for row_obj in rows:
            row = row_obj["data"]
            item = {
                "external_sku_code": row.get("SKU ID", "").strip(),
                "hsn_code": row.get("HSN Code", "").strip(),
                "base_price": self._parse_float(row.get("Base Price", "")),
                "tax_percent": self._parse_float(row.get("Tax", "")),
                "igst": self._parse_float(row.get("IGST", "")),
                "cgst": self._parse_float(row.get("CGST", "")),
                "sgst": self._parse_float(row.get("SGST", "")),
                "selling_price": self._parse_float(row.get("Selling Price", ""))
            }
            normalized["items"].append(item)
            
            normalized["total_base_price"] += item["base_price"]
            normalized["total_igst"] += item["igst"]
            normalized["total_cgst"] += item["cgst"]
            normalized["total_sgst"] += item["sgst"]
            normalized["total_tax"] += item["igst"] + item["cgst"] + item["sgst"]
            
        return normalized

class ShopDeckTaxAdapter:
    def __init__(self, record_service, error_service, summary_service):
        self.record_service = record_service
        self.error_service = error_service
        self.summary_service = summary_service
        self.reader = ShopDeckTaxReader()
        self.validator = ShopDeckTaxValidator()
        self.mapper = ShopDeckTaxMapper()

    async def parse_and_ingest(self, file_content: bytes, job_id: UUID, created_by: UUID) -> None:
        grouped_raw_list = self.reader.read(file_content)
        
        records_to_create = []
        errors_to_log = []
        
        for grouped_raw in grouped_raw_list:
            validation_errors = self.validator.validate(grouped_raw)
            if validation_errors:
                for err in validation_errors:
                    errors_to_log.append(ImportErrorCreate(
                        import_job_id=job_id,
                        error_code=err["error_code"],
                        error_message=err["error_message"],
                        row_number=err.get("row_number")
                    ))
                continue
                
            normalized = self.mapper.map(grouped_raw)
            raw_dicts = [r["data"] for r in grouped_raw["rows"]]
            
            records_to_create.append(
                ImportRecordCreate(
                    import_job_id=job_id,
                    record_type="TAX_INVOICE",
                    raw_data={"rows": raw_dicts},
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

        await self.summary_service.generate_initial_summary(job_id=job_id, total_records=len(grouped_raw_list), created_by=created_by)
        await self.summary_service.update_summary_stats(
            job_id=job_id,
            successful=len(records_to_create),
            failed=len(grouped_raw_list) - len(records_to_create),
            duplicate=0,
            updated_by=created_by
        )
