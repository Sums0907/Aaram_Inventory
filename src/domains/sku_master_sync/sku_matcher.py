from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.foundation.enums.item_type import ItemType
from src.foundation.enums.status import GenericStatus

class SkuMatcher:
    """
    Handles identity matching against the database using shopdeck_sku_id.
    Classifies rows into NEW, EXISTING, and MISSING.
    Enforces SKU-008 (Duplicate Sku Id Detection) and SKU-010 (Product Code Collision Detection).
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    async def match(self, parsed_rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[SKUModel], List[str]]:
        """
        Returns (new_rows, existing_rows, missing_skus, validation_errors)
        """
        errors = []
        
        # 1. Check for duplicates in CSV (SKU-008)
        seen_sku_ids = set()
        valid_rows = []
        
        for row in parsed_rows:
            sku_id = row["shopdeck_sku_id"]
            
            # SKU-008: Duplicate Sku Id Detection
            if sku_id in seen_sku_ids:
                errors.append(f"Validation Error: Duplicate Sku Id '{sku_id}' in CSV.")
                continue
            seen_sku_ids.add(sku_id)
            
            # Note: Under multi-variant architecture, multiple SKUs can share the same product_code
            valid_rows.append(row)
            
        if errors:
            return [], [], [], errors
            
        from sqlalchemy.orm import selectinload
        
        # 2. Fetch existing DB SKUs for FG domain
        stmt = select(SKUModel).join(ProductModel).where(ProductModel.item_type == ItemType.FINISHED_GOODS).options(
            selectinload(SKUModel.product),
            selectinload(SKUModel.pricing),
            selectinload(SKUModel.packaging)
        )
        all_fg_skus = (await self.db.execute(stmt)).scalars().all()
        
        db_sku_map = {sku.shopdeck_sku_id: sku for sku in all_fg_skus if sku.shopdeck_sku_id}
        
        new_rows = []
        existing_rows = []
        incoming_sku_ids = set([r["shopdeck_sku_id"] for r in valid_rows])
        
        for row in valid_rows:
            sku_id = row["shopdeck_sku_id"]
            if sku_id in db_sku_map:
                existing_rows.append({
                    "csv_row": row,
                    "db_sku": db_sku_map[sku_id]
                })
            else:
                new_rows.append(row)
            
        # 4. Find MISSING SKUs (in DB, not in CSV, and currently ACTIVE)
        missing_skus = []
        for sku in all_fg_skus:
            if sku.shopdeck_sku_id and sku.shopdeck_sku_id not in incoming_sku_ids:
                if sku.status != GenericStatus.INACTIVE:
                    missing_skus.append(sku)
                    
        return new_rows, existing_rows, missing_skus, []
