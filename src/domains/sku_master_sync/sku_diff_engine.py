from typing import List, Dict, Any, Tuple
from decimal import Decimal
from src.foundation.enums.status import GenericStatus

class SkuDiffEngine:
    """
    Compares incoming ShopDeck fields against existing database records.
    Never mutates the database. Generates a diff report for dry runs.
    """
    
    @staticmethod
    def _float_equal(val1: float, val2: Any) -> bool:
        if val1 is None: val1 = 0.0
        if val2 is None: val2 = 0.0
        try:
            return abs(float(val1) - float(val2)) < 0.01
        except (ValueError, TypeError):
            return False

    @classmethod
    def calculate_diffs(cls, existing_rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Returns (updated_rows, ignored_rows)
        """
        updated_rows = []
        ignored_rows = []
        
        for record in existing_rows:
            csv_row = record["csv_row"]
            db_sku = record["db_sku"]
            db_product = db_sku.product
            
            changes = {}
            
            # Mutable Fields check
            if db_product.product_code != csv_row["product_code"]:
                changes["product_code"] = {"old": db_product.product_code, "new": csv_row["product_code"]}
            if db_product.product_name != csv_row["name"]:
                changes["product_name"] = {"old": db_product.product_name, "new": csv_row["name"]}
                
            # Pricing
            db_pricing = db_sku.pricing
            if db_pricing:
                if not cls._float_equal(db_pricing.selling_price, csv_row["selling_price"]):
                    changes["selling_price"] = {"old": float(db_pricing.selling_price), "new": csv_row["selling_price"]}
                if not cls._float_equal(db_pricing.mrp, csv_row["mrp"]):
                    changes["mrp"] = {"old": float(db_pricing.mrp), "new": csv_row["mrp"]}
                if not cls._float_equal(db_pricing.cost_price, csv_row["cost_price"]):
                    changes["cost_price"] = {"old": float(db_pricing.cost_price), "new": csv_row["cost_price"]}
                if not cls._float_equal(db_pricing.gst_percentage, csv_row["gst_percentage"]):
                    changes["gst_percentage"] = {"old": float(db_pricing.gst_percentage), "new": csv_row["gst_percentage"]}
            else:
                # Need to create pricing if it doesn't exist
                if csv_row["selling_price"] or csv_row["mrp"] or csv_row["cost_price"]:
                    changes["pricing"] = {"old": "None", "new": "Pricing object to create"}
                    
            # Packaging
            db_packaging = db_sku.packaging
            if db_packaging:
                if not cls._float_equal(db_packaging.length, csv_row["length"]):
                    changes["length"] = {"old": float(db_packaging.length), "new": csv_row["length"]}
                if not cls._float_equal(db_packaging.breadth, csv_row["breadth"]):
                    changes["breadth"] = {"old": float(db_packaging.breadth), "new": csv_row["breadth"]}
                if not cls._float_equal(db_packaging.height, csv_row["height"]):
                    changes["height"] = {"old": float(db_packaging.height), "new": csv_row["height"]}
                if not cls._float_equal(db_packaging.weight, csv_row["weight"]):
                    changes["weight"] = {"old": float(db_packaging.weight), "new": csv_row["weight"]}
            else:
                if csv_row["length"] or csv_row["breadth"] or csv_row["height"] or csv_row["weight"]:
                    changes["packaging"] = {"old": "None", "new": "Packaging object to create"}

            # Reactivation (SKU-011)
            if db_sku.status == GenericStatus.INACTIVE:
                changes["status"] = {"old": "INACTIVE", "new": "ACTIVE"}

            if changes:
                updated_rows.append({
                    "sku_id": csv_row["shopdeck_sku_id"],
                    "changes": changes,
                    "db_sku": db_sku,
                    "csv_row": csv_row
                })
            else:
                ignored_rows.append({
                    "sku_id": csv_row["shopdeck_sku_id"],
                    "csv_row": csv_row,
                    "reason": "ShopDeck Quantity is not inventory data"
                })
                
        return updated_rows, ignored_rows

    @classmethod
    def format_report(cls, new_rows: List[Dict], updated_rows: List[Dict], archived_skus: List[Any], ignored_rows: List[Dict], errors: List[str]) -> str:
        report = []
        report.append("SHOPDECK SKU CATALOGUE SYNC REPORT\n")
        report.append(f"Created:\n{len(new_rows)}\n")
        report.append(f"Updated:\n{len(updated_rows)}\n")
        report.append(f"Archived:\n{len(archived_skus)}\n")
        report.append(f"Ignored:\n{len(ignored_rows)}\n")
        report.append(f"Failed:\n{len(errors)}\n")
        
        for u in updated_rows:
            report.append(f"SKU ID:\n{u['sku_id']}\n")
            report.append("Changes:")
            for field, change in u['changes'].items():
                report.append(f"{field}:\n{change['old']} \u2192 {change['new']}\n")
        
        for i in ignored_rows:
            report.append(f"SKU ID:\n{i['sku_id']}\n")
            report.append("Result:\nIGNORED")
            report.append(f"Reason:\n{i['reason']}\n")
            
        for e in errors:
            report.append(f"Error:\n{e}\n")
            
        return "\n".join(report)
