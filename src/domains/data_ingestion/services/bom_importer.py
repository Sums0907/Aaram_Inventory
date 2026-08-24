import uuid
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.masters.models.bom import BOMModel, BOMItemModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.data_ingestion.services.master_data_importer import (
    BaseMasterDataImporter, ImportResult, ImportRowResult, ImportAction
)

class BOMImporter(BaseMasterDataImporter):
    
    def _safe_float(self, val: Any) -> float:
        try:
            return float(val) if val else 0.0
        except (ValueError, TypeError):
            return 0.0

    async def import_data(self, data: List[Dict[str, Any]], is_dry_run: bool = True) -> ImportResult:
        result = ImportResult(entity_type="BOM", total_records=len(data))
        
        # 1. Group data by BOM Number
        grouped_boms: Dict[str, List[tuple[int, Dict[str, Any]]]] = {}
        for idx, row in enumerate(data):
            bom_num = str(row.get("BOM Number", "")).strip()
            if not bom_num:
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=idx + 1, action=ImportAction.FAILED,
                    errors=["Missing required field 'BOM Number'"]
                ))
                continue
            if bom_num not in grouped_boms:
                grouped_boms[bom_num] = []
            grouped_boms[bom_num].append((idx + 1, row))
            
        # Pre-fetch all necessary SKUs and UOMs
        skus_list = (await self.session.execute(select(SKUModel))).scalars().all()
        skus_by_item_code = {s.item_code: s for s in skus_list}
        skus_by_sku_code = {s.sku_code: s for s in skus_list if s.sku_code}
        
        uoms = (await self.session.execute(select(UnitOfMeasureModel))).scalars().all()
        uoms_by_code = {u.unit_code: u for u in uoms}
        
        # Pre-fetch Active BOMs to compare content
        active_boms_stmt = select(BOMModel).options(selectinload(BOMModel.items)).where(BOMModel.effective_to.is_(None))
        active_boms_list = (await self.session.execute(active_boms_stmt)).scalars().all()
        active_boms_by_num = {b.bom_number: b for b in active_boms_list}
        
        for bom_num, rows in grouped_boms.items():
            # Basic validation
            first_row_idx, first_row = rows[0]
            bom_name = str(first_row.get("BOM Name", first_row.get("BoM Name", ""))).strip()
            
            target_sku_code = str(first_row.get("Finished SKU", "")).strip()
            target_qty = int(self._safe_float(first_row.get("Base Quantity")) or 1)
            
            # Resolve Target SKU
            target_sku = skus_by_sku_code.get(target_sku_code) or skus_by_item_code.get(target_sku_code)
            if not target_sku:
                for idx, _ in rows:
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=idx, action=ImportAction.FAILED, identifier=bom_num,
                        errors=[f"Target SKU '{target_sku_code}' not found."]
                    ))
                continue
                
            # Parse Components
            parsed_components = []
            has_error = False
            seen_components = set()
            for idx, row in rows:
                comp_code = str(row.get("Component SKU", "")).strip()
                comp_qty = self._safe_float(row.get("Component Quantity"))
                wastage = self._safe_float(row.get("Wastage %"))
                tolerance = self._safe_float(row.get("Tolerance %", 0.0))
                uom_code = str(row.get("Component UOM", "")).strip() # Fallback if provided, else component's default
                
                comp_sku = skus_by_sku_code.get(comp_code) or skus_by_item_code.get(comp_code)
                if not comp_sku:
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(row_index=idx, action=ImportAction.FAILED, identifier=bom_num, errors=[f"Component SKU '{comp_code}' not found."]))
                    has_error = True
                    continue
                
                # Check exact duplicate line in the same import
                dedup_key = (comp_sku.id, comp_qty)
                if dedup_key in seen_components:
                    result.ignored_count += 1
                    result.row_results.append(ImportRowResult(row_index=idx, action=ImportAction.IGNORED, identifier=bom_num, errors=["Exact duplicate component line in import file."]))
                    continue
                seen_components.add(dedup_key)
                    
                uom_id = uoms_by_code[uom_code].id if uom_code in uoms_by_code else comp_sku.uom_id
                
                parsed_components.append({
                    "sku_id": comp_sku.id,
                    "qty": comp_qty,
                    "wastage": wastage,
                    "tolerance": tolerance,
                    "uom_id": uom_id
                })
                
            if has_error:
                # If any line failed, the whole BOM fails (except the ones marked ignored above).
                # We already appended FAILED for the bad lines. But we shouldn't create the BOM.
                for idx, _ in rows:
                    if not any(r.row_index == idx for r in result.row_results):
                        result.failed_count += 1
                        result.row_results.append(ImportRowResult(row_index=idx, action=ImportAction.FAILED, identifier=bom_num, errors=["BOM aborted due to errors in other lines."]))
                continue
                
            # Content-based versioning
            existing_active_bom = active_boms_by_num.get(bom_num)
            
            needs_new_version = True
            new_version_num = 1
            
            if existing_active_bom:
                new_version_num = existing_active_bom.version + 1
                
                # Compare exact content
                content_matches = True
                if existing_active_bom.target_item_id != target_sku.id: content_matches = False
                if existing_active_bom.target_quantity != target_qty: content_matches = False
                
                if len(existing_active_bom.items) != len(parsed_components):
                    content_matches = False
                else:
                    # Deep compare items
                    # Sort both by sku_id then qty for stable comparison
                    db_items = sorted(existing_active_bom.items, key=lambda i: (str(i.component_item_id), float(i.quantity)))
                    im_items = sorted(parsed_components, key=lambda i: (str(i["sku_id"]), float(i["qty"])))
                    
                    for db_i, im_i in zip(db_items, im_items):
                        if db_i.component_item_id != im_i["sku_id"]: content_matches = False
                        if float(db_i.quantity) != float(im_i["qty"]): content_matches = False
                        if float(db_i.wastage_percentage) != float(im_i["wastage"]): content_matches = False
                        if db_i.uom_id != im_i["uom_id"]: content_matches = False
                        
                if content_matches:
                    needs_new_version = False
            
            if not needs_new_version:
                # In-place update metadata if recipe hasn't changed but name has
                if not is_dry_run and existing_active_bom and bom_name:
                    if existing_active_bom.bom_name != bom_name:
                        existing_active_bom.bom_name = bom_name
                        self.session.add(existing_active_bom)

                for idx, _ in rows:
                    if not any(r.row_index == idx for r in result.row_results):
                        result.ignored_count += 1
                        result.row_results.append(ImportRowResult(row_index=idx, action=ImportAction.IGNORED, identifier=bom_num))
            else:
                if not is_dry_run:
                    if existing_active_bom:
                        # Sunset old version
                        existing_active_bom.effective_to = datetime.utcnow().date()
                        existing_active_bom.status = "ARCHIVED"
                        
                    new_bom = BOMModel(
                        id=uuid.uuid4(),
                        bom_number=bom_num,
                        bom_name=bom_name,
                        target_item_id=target_sku.id,
                        target_quantity=target_qty,
                        version=new_version_num,
                        status="ACTIVE",
                        effective_from=datetime.utcnow().date()
                    )
                    
                    for comp in parsed_components:
                        item = BOMItemModel(
                            id=uuid.uuid4(),
                            bom_id=new_bom.id,
                            component_item_id=comp["sku_id"],
                            quantity=comp["qty"],
                            wastage_percentage=comp["wastage"],
                            tolerance_percentage=comp["tolerance"],
                            uom_id=comp["uom_id"],
                            unit_of_measure="-" # Kept for legacy compatibility if needed
                        )
                        new_bom.items.append(item)
                    
                    self.session.add(new_bom)
                    active_boms_by_num[bom_num] = new_bom
                    
                for idx, _ in rows:
                    if not any(r.row_index == idx for r in result.row_results):
                        result.created_count += 1
                        result.row_results.append(ImportRowResult(row_index=idx, action=ImportAction.CREATED, identifier=bom_num))
                        
        if not is_dry_run:
            await self.session.flush()
            
        return result
