import uuid
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.foundation.enums.status import GenericStatus
from src.foundation.enums import ItemType
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.pricing import PricingModel
from src.domains.masters.models.packaging import PackagingModel
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.data_ingestion.services.master_data_importer import (
    BaseMasterDataImporter, ImportResult, ImportRowResult, ImportAction
)
from src.domains.masters.services.category_ownership import CategoryOwnershipResolver

class ProductSKUImporter(BaseMasterDataImporter):
    
    def _safe_float(self, val: Any) -> float:
        try:
            return float(val) if val else 0.0
        except (ValueError, TypeError):
            return 0.0

    async def import_data(self, data: List[Dict[str, Any]], is_dry_run: bool = True) -> ImportResult:
        result = ImportResult(entity_type="PRODUCT_SKU", total_records=len(data))
        
        # Pre-fetch Products, SKUs, Categories, UOMs
        products_stmt = select(ProductModel).options(selectinload(ProductModel.skus))
        products_list = (await self.session.execute(products_stmt)).scalars().all()
        products_by_code = {p.product_code: p for p in products_list}
        
        skus_stmt = select(SKUModel).options(selectinload(SKUModel.pricing), selectinload(SKUModel.packaging))
        skus_list = (await self.session.execute(skus_stmt)).scalars().all()
        skus_by_item_code = {s.item_code: s for s in skus_list}
        skus_by_sku_code = {s.sku_code: s for s in skus_list if s.sku_code}
        skus_by_barcode = {s.barcode: s for s in skus_list if s.barcode}
        
        cats = (await self.session.execute(select(CategoryModel))).scalars().all()
        cats_by_code = {c.category_code: c for c in cats}
        
        uoms = (await self.session.execute(select(UnitOfMeasureModel))).scalars().all()
        uoms_by_code = {u.unit_code: u for u in uoms}
        
        for idx, row in enumerate(data):
            row_num = idx + 1
            
            # Identity codes
            item_code = str(row.get("Item Code") or row.get("Sku Id", "")).strip()
            # Product Code may be absent in Raw_Materials sheet — derive from Item Code (1:1 mapping)
            product_code = str(row.get("Product Code", "")).strip() or item_code
            sku_code = str(row.get("Sku Id", "")).strip()
            barcode = str(row.get("Barcode", "")).strip()
            
            if not item_code:
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.FAILED,
                    errors=["Missing required field 'Item Code'"]
                ))
                continue
                
            # Mutable fields
            prod_name = str(row.get("Name", "")).strip()
            if not prod_name:
                prod_name = str(row.get("Master Item Name", "")).strip()
            if not prod_name:
                prod_name = product_code
                
            brand = str(row.get("attr_Brand", "")).strip()
            desc = str(row.get("Description", "")).strip()
            size = str(row.get("Size", "")).strip()
            color = str(row.get("Colour", "")).strip()
            
            selling_price = self._safe_float(row.get("Selling Price"))
            mrp = self._safe_float(row.get("MRP"))
            cost_price = self._safe_float(row.get("Cost Price"))
            gst = self._safe_float(row.get("GST %"))
            hsn = str(row.get("HSN Code", "")).strip()
            
            p_len = self._safe_float(row.get("Packaging Length (in cm)"))
            p_bre = self._safe_float(row.get("Packaging Breadth (in cm)"))
            p_hei = self._safe_float(row.get("Packaging Height (in cm)"))
            p_wei = self._safe_float(row.get("Packaging Weight (in kg)"))
            
            cat_code = str(row.get("Category Code", "")).strip()
            uom_code = str(row.get("Base UoM Code", "")).strip()
            
            cat_id = cats_by_code[cat_code].id if cat_code in cats_by_code else None
            uom_id = uoms_by_code[uom_code].id if uom_code in uoms_by_code else None
            
            status_str = str(row.get("Status", "ACTIVE")).strip().upper()
            status = GenericStatus.ACTIVE if status_str == "ACTIVE" else GenericStatus.INACTIVE
            
            # ── FG Boundary Guard ──────────────────────────────────────────────────────
            # A non-empty 'Sku Id' column is the ShopDeck Finished Goods identifier.
            # The Raw Material Sub-Engine must never create FINISHED_GOODS records.
            # FG SKUs belong exclusively to the SKU Master Data Sub-Engine (future).
            if row.get("Sku Id") and str(row.get("Sku Id")).strip():
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.FAILED, identifier=item_code,
                    errors=[
                        f"Row '{item_code}' contains a 'Sku Id' field which identifies a "
                        f"Finished Goods SKU. Finished Goods SKUs are managed by the "
                        f"SKU Master Data Sub-Engine, not the Raw Material importer."
                    ]
                ))
                continue

            # Verify category domain if category is provided
            if cat_code:
                try:
                    resolver = CategoryOwnershipResolver(self.session)
                    # Use cats_by_code as memory_cache for unresolved categories in same transaction if needed,
                    # but categories must be pre-created before item import.
                    resolved = await resolver.resolve(cat_code)
                    if resolved["domain"] == "FINISHED_GOODS":
                        result.failed_count += 1
                        result.row_results.append(ImportRowResult(
                            row_index=row_num, action=ImportAction.FAILED, identifier=item_code,
                            errors=[
                                f"Category '{cat_code}' resolves to the Finished Goods taxonomy. "
                                f"Raw Material items must be assigned to Operational categories."
                            ]
                        ))
                        continue
                except ValueError as e:
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=row_num, action=ImportAction.FAILED, identifier=item_code,
                        errors=[str(e)]
                    ))
                    continue

            item_type = ItemType.RAW_MATERIAL
            
            # Check Product Identity
            prod = products_by_code.get(product_code)
            if not prod:
                if not is_dry_run:
                    prod = ProductModel(
                        id=uuid.uuid4(),
                        product_code=product_code,
                        product_name=prod_name,
                        brand=brand,
                        description=desc,
                        item_type=item_type,
                        status=status,
                        category_id=cat_id
                    )
                    self.session.add(prod)
                    products_by_code[product_code] = prod
            
            # Check SKU Identity
            sku = skus_by_item_code.get(item_code)
            
            if not sku:
                # Validate that barcode doesn't belong to another SKU
                if barcode and barcode in skus_by_barcode:
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=row_num, action=ImportAction.FAILED, identifier=item_code,
                        errors=[f"Barcode '{barcode}' already exists for another SKU."]
                    ))
                    continue
                
                # Check SKU Code conflict
                if sku_code and sku_code in skus_by_sku_code:
                     result.failed_count += 1
                     result.row_results.append(ImportRowResult(
                         row_index=row_num, action=ImportAction.FAILED, identifier=item_code,
                         errors=[f"SKU Code '{sku_code}' already exists for another SKU."]
                     ))
                     continue

                if not is_dry_run:
                    sku = SKUModel(
                        id=uuid.uuid4(),
                        item_code=item_code,
                        sku_code=sku_code if sku_code else None,
                        product_id=prod.id,
                        barcode=barcode if barcode else None,
                        size=size,
                        color=color,
                        uom_id=uom_id,
                        status=status,
                        attribute_values={}
                    )
                    pricing = PricingModel(
                        id=uuid.uuid4(), sku_id=sku.id, selling_price=selling_price, mrp=mrp, cost_price=cost_price, gst_percentage=gst, hsn_code=hsn
                    )
                    packaging = PackagingModel(
                        id=uuid.uuid4(), sku_id=sku.id, length=p_len, breadth=p_bre, height=p_hei, weight=p_wei
                    )
                    self.session.add(sku)
                    self.session.add(pricing)
                    self.session.add(packaging)
                    
                    skus_by_item_code[item_code] = sku
                    if barcode: skus_by_barcode[barcode] = sku
                    if sku_code: skus_by_sku_code[sku_code] = sku
                    
                result.created_count += 1
                result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.CREATED, identifier=item_code))
            else:
                # SKU exists. Enforce Immutable Identity
                if (barcode and sku.barcode and barcode != sku.barcode) or (sku_code and sku.sku_code and sku_code != sku.sku_code):
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=row_num, action=ImportAction.FAILED, identifier=item_code,
                        errors=["Cannot change immutable identity codes (sku_code, barcode) for existing SKU."]
                    ))
                    continue
                
                # Compare for Exact match
                pr = sku.pricing
                pa = sku.packaging
                
                is_exact = True
                if sku.size != size or sku.color != color or sku.status != status: is_exact = False
                if not pr or pr.selling_price != selling_price or pr.mrp != mrp or pr.cost_price != cost_price or pr.gst_percentage != gst: is_exact = False
                if not pa or pa.length != p_len or pa.breadth != p_bre or pa.height != p_hei or pa.weight != p_wei: is_exact = False
                
                if is_exact:
                    result.ignored_count += 1
                    result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.IGNORED, identifier=item_code))
                else:
                    if not is_dry_run:
                        sku.size = size
                        sku.color = color
                        sku.status = status
                        # Protected fields: category_id (on product), uom_id (on sku) are NOT updated.
                        
                        if pr:
                            pr.selling_price = selling_price
                            pr.mrp = mrp
                            pr.cost_price = cost_price
                            pr.gst_percentage = gst
                            pr.hsn_code = hsn
                        if pa:
                            pa.length = p_len
                            pa.breadth = p_bre
                            pa.height = p_hei
                            pa.weight = p_wei
                            
                    result.updated_count += 1
                    result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.UPDATED, identifier=item_code))
                    
        if not is_dry_run:
            await self.session.flush()
            
        return result
