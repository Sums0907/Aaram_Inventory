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
        seen_product_codes = {} # product_code -> shopdeck_sku_id
        
        valid_rows = []
        
        for row in parsed_rows:
            sku_id = row["shopdeck_sku_id"]
            product_code = row["product_code"]
            
            # SKU-008: Duplicate Sku Id Detection
            if sku_id in seen_sku_ids:
                errors.append(f"Validation Error: Duplicate Sku Id '{sku_id}' in CSV.")
                continue
            seen_sku_ids.add(sku_id)
            
            # SKU-010: Product Code Collision Detection in CSV
            if product_code in seen_product_codes and seen_product_codes[product_code] != sku_id:
                errors.append(f"Validation Error: Product Code '{product_code}' is mapped to multiple Sku Ids in CSV ({seen_product_codes[product_code]} and {sku_id}).")
                continue
            seen_product_codes[product_code] = sku_id
            
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
                
        # 3. Product Code Collision Detection against DB (SKU-010)
        # Check if any NEW or EXISTING row uses a Product Code that belongs to a different ShopDeck Sku Id in DB
        db_product_code_stmt = select(ProductModel).where(ProductModel.item_type == ItemType.FINISHED_GOODS)
        all_fg_products = (await self.db.execute(db_product_code_stmt)).scalars().all()
        db_product_code_map = {prod.product_code: prod for prod in all_fg_products}
        
        for row in valid_rows:
            pc = row["product_code"]
            sku_id = row["shopdeck_sku_id"]
            
            if pc in db_product_code_map:
                existing_prod = db_product_code_map[pc]
                # Is there a SKU mapped to this product?
                # We need to ensure we don't steal product codes across DIFFERENT shopdeck_sku_ids
                # If existing product is linked to a SKU that has a DIFFERENT shopdeck_sku_id, collision.
                linked_skus = [sku for sku in all_fg_skus if sku.product_id == existing_prod.id]
                for l_sku in linked_skus:
                    if l_sku.shopdeck_sku_id and l_sku.shopdeck_sku_id != sku_id:
                        errors.append(f"Validation Error: Product Code '{pc}' is already used by DB Sku Id '{l_sku.shopdeck_sku_id}'. Cannot reassign to '{sku_id}'.")
        
        if errors:
            return [], [], [], errors
            
        # 4. Find MISSING SKUs (in DB, not in CSV, and currently ACTIVE)
        missing_skus = []
        for sku in all_fg_skus:
            if sku.shopdeck_sku_id and sku.shopdeck_sku_id not in incoming_sku_ids:
                if sku.status != GenericStatus.INACTIVE:
                    missing_skus.append(sku)
                    
        return new_rows, existing_rows, missing_skus, []
