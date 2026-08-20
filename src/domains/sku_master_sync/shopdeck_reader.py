import csv
from typing import List, Dict, Any
from io import StringIO

class ShopDeckReader:
    """
    Parses ShopDeck Catalogue CSV files and normalizes data for the SKU Master Sync Engine.
    Enforces SKU-SYNC-RULE-001 by aggressively dropping the Quantity field.
    """
    
    EXPECTED_COLUMNS = [
        "Sku Id",
        "Product Code",
        "Name"
    ]
    
    @classmethod
    def parse_csv(cls, file_content: str) -> List[Dict[str, Any]]:
        """
        Parse raw CSV string into a list of normalized dictionaries.
        """
        reader = csv.DictReader(StringIO(file_content.strip()))
        
        if not reader.fieldnames:
            raise ValueError("Empty or invalid CSV provided")
            
        # Validate essential columns
        missing_columns = [col for col in cls.EXPECTED_COLUMNS if col not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Missing required columns in ShopDeck CSV: {missing_columns}")
            
        parsed_rows = []
        for row_num, row in enumerate(reader, start=2):
            normalized_row = cls._normalize_row(row)
            if not normalized_row.get("shopdeck_sku_id"):
                raise ValueError(f"Row {row_num}: Missing 'Sku Id'")
            parsed_rows.append(normalized_row)
            
        return parsed_rows
        
    @classmethod
    def _normalize_row(cls, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Normalizes a single CSV row into the expected dict structure, ensuring Quantity is dropped.
        """
        # SKU-SYNC-RULE-001: Drop Quantity immediately
        if "Quantity" in row:
            del row["Quantity"]
            
        # Extract fields
        shopdeck_sku_id = row.get("Sku Id", "").strip()
        product_code = row.get("Product Code", "").strip()
        name = row.get("Name", "").strip()
        selling_price = cls._parse_float(row.get("Selling Price"))
        mrp = cls._parse_float(row.get("MRP"))
        cost_price = cls._parse_float(row.get("Cost Price"))
        gst_percentage = cls._parse_float(row.get("GST %"))
        
        length = cls._parse_float(row.get("Packaging Length (in cm)") or row.get("Packaging Length"))
        breadth = cls._parse_float(row.get("Packaging Breadth (in cm)") or row.get("Packaging Breadth"))
        height = cls._parse_float(row.get("Packaging Height (in cm)") or row.get("Packaging Height"))
        weight = cls._parse_float(row.get("Packaging Weight (in kg)") or row.get("Packaging Weight"))
        
        category_path = row.get("Category Path", "").strip()
        
        # Attributes JSON parsing (could be provided as a stringified JSON or plain string)
        attributes_raw = row.get("Attributes", "").strip()
        # For this engine, we will pass attributes as a raw string or handle parsing in the validator if needed
        # We'll just pass it along
        
        return {
            "shopdeck_sku_id": shopdeck_sku_id,
            "product_code": product_code,
            "name": name,
            "selling_price": selling_price,
            "mrp": mrp,
            "cost_price": cost_price,
            "gst_percentage": gst_percentage,
            "length": length,
            "breadth": breadth,
            "height": height,
            "weight": weight,
            "category_path": category_path,
            "attributes_raw": attributes_raw
        }
        
    @staticmethod
    def _parse_float(value: Any) -> float:
        if not value:
            return 0.0
        try:
            return float(str(value).strip().replace(',', ''))
        except ValueError:
            return 0.0
