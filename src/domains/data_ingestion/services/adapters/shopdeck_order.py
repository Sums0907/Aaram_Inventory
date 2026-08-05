import csv
from uuid import UUID
from datetime import datetime
from typing import Dict, Any, List, Tuple
from src.domains.data_ingestion.schemas.import_record import ImportRecordCreate
from src.domains.data_ingestion.schemas.import_error import ImportErrorCreate

class ShopDeckOrderReader:
    def read(self, file_content: bytes) -> List[Dict[str, Any]]:
        content_str = file_content.decode('utf-8-sig')
        lines = content_str.splitlines()
        
        if len(lines) > 2 and "Order Reconciliation Report" in lines[0]:
            lines = lines[2:]
            
        reader = csv.DictReader(lines)
        
        # Group by Order ID
        grouped_orders: Dict[str, Dict[str, Any]] = {}
        row_number = 3
        
        for row in reader:
            row_number += 1
            order_id = row.get("Order ID", "").strip()
            
            if not order_id and not any(row.values()):
                continue # Skip completely empty rows
                
            if order_id not in grouped_orders:
                grouped_orders[order_id] = {
                    "order_id": order_id,
                    "rows": [],
                    "first_row_number": row_number
                }
            
            grouped_orders[order_id]["rows"].append({
                "data": row,
                "row_number": row_number
            })
            
        return list(grouped_orders.values())

class ShopDeckOrderValidator:
    def validate(self, grouped_raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        errors = []
        if not grouped_raw.get("order_id"):
            errors.append({
                "error_code": "MISSING_ORDER_ID",
                "error_message": "Row is missing Order ID",
                "row_number": grouped_raw.get("first_row_number")
            })
        return errors

class ShopDeckOrderMapper:
    def _parse_float(self, value: str) -> float:
        if not value or not str(value).strip():
            return 0.0
        try:
            return float(str(value).replace(',', '').strip())
        except ValueError:
            return 0.0

    def _parse_int(self, value: str) -> int:
        if not value or not str(value).strip():
            return 0
        try:
            return int(str(value).replace(',', '').strip())
        except ValueError:
            return 0

    def _parse_date(self, value: str) -> str:
        if not value or not str(value).strip():
            return ""
        try:
            parsed = datetime.strptime(str(value).strip(), "%d-%m-%Y")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            return str(value).strip()

    def map(self, grouped_raw: Dict[str, Any]) -> Dict[str, Any]:
        rows = grouped_raw["rows"]
        first_row = rows[0]["data"]
        
        normalized = {
            "external_order_id": grouped_raw["order_id"],
            "order_date": self._parse_date(first_row.get("Order Creation Date", "")),
            "channel": first_row.get("Channel", "").strip(),
            "status": first_row.get("Order Status", "").strip(),
            
            "customer_name": first_row.get("Customer Name", "").strip(),
            "customer_mobile": first_row.get("Mobile", "").strip(),
            
            "shipping_address": first_row.get("Address", "").strip(),
            "shipping_pincode": first_row.get("Pincode", "").strip(),
            "shipping_city": first_row.get("City", "").strip(),
            "shipping_state": first_row.get("State", "").strip(),
            
            "payment_method": first_row.get("Payment Method", "").strip(),
            
            "gross_amount": self._parse_float(first_row.get("Invoice Total (Incl. Tax)", "")),
            "discount_amount": self._parse_float(first_row.get("Prepaid Discount", "")),
            "shipping_fee": self._parse_float(first_row.get("Delivery Fees (Incl. Tax)", "")),
            "cod_fee": self._parse_float(first_row.get("COD Charges (Incl. Tax)", "")),
            # Approximate net_amount for now
            "net_amount": self._parse_float(first_row.get("Invoice Total (Incl. Tax)", "")),
            
            "items": []
        }
        
        for row_obj in rows:
            row = row_obj["data"]
            normalized["items"].append({
                "external_sku_code": row.get("SKU Code", "").strip(),
                "quantity": self._parse_int(row.get("Quantity", "")),
                "unit_price": self._parse_float(row.get("Product Amount (Incl. Tax)", "")),
                "tax_amount": self._parse_float(row.get("Product Tax Amount", ""))
            })
            
        return normalized

class ShopDeckOrderAdapter:
    def __init__(self, record_service, error_service, summary_service):
        self.record_service = record_service
        self.error_service = error_service
        self.summary_service = summary_service
        self.reader = ShopDeckOrderReader()
        self.validator = ShopDeckOrderValidator()
        self.mapper = ShopDeckOrderMapper()

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
            # Store just the pure dicts in raw_data
            raw_dicts = [r["data"] for r in grouped_raw["rows"]]
            
            records_to_create.append(
                ImportRecordCreate(
                    import_job_id=job_id,
                    record_type="SALES_ORDER",
                    raw_data={"rows": raw_dicts},
                    status="VALID",
                    normalized_data=normalized
                )
            )

        # Batch insert
        if records_to_create:
            batch_size = 500
            for i in range(0, len(records_to_create), batch_size):
                await self.record_service.create_records_batch(records_to_create[i:i + batch_size], created_by)

        if errors_to_log:
            await self.error_service.log_errors_batch(errors_to_log, created_by)

        # Update summary
        await self.summary_service.generate_initial_summary(
            job_id=job_id,
            total_records=len(grouped_raw_list),
            created_by=created_by
        )
        await self.summary_service.update_summary_stats(
            job_id=job_id,
            successful=len(records_to_create),
            failed=len(grouped_raw_list) - len(records_to_create),
            duplicate=0,
            updated_by=created_by
        )
