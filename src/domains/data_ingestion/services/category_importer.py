import uuid
from typing import List, Dict, Any
from sqlalchemy import select
from src.foundation.enums.status import GenericStatus
from src.domains.masters.models.category import CategoryModel
from src.domains.data_ingestion.services.master_data_importer import (
    BaseMasterDataImporter, ImportResult, ImportRowResult, ImportAction
)

from src.domains.masters.services.category_ownership import CategoryOwnershipResolver

ROOT_CATEGORIES = {
    "FG": "Finished Goods",
    "RM": "Raw Materials",
    "PKG": "Packaging",
    "CON": "Consumables",
    "AST": "Assets"
}

class CategoryImporter(BaseMasterDataImporter):
    
    async def import_data(self, data: List[Dict[str, Any]], is_dry_run: bool = True) -> ImportResult:
        result = ImportResult(entity_type="CATEGORY", total_records=len(data))
        
        # Pre-fetch existing categories
        stmt = select(CategoryModel)
        existing_cats_list = (await self.session.execute(stmt)).scalars().all()
        existing_cats = {c.category_code: c for c in existing_cats_list}
        
        for idx, row in enumerate(data):
            row_num = idx + 1
            code = row.get("Category Code")
            if not code:
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.FAILED, 
                    errors=["Missing required field 'Category Code'"]
                ))
                continue
            
            code = str(code).strip()
            name = str(row.get("Category Name", "")).strip()
            parent_code = row.get("Parent Category Code")
            if parent_code:
                parent_code = str(parent_code).strip()
            desc = str(row.get("Description", "")).strip()
            status_str = str(row.get("Status", "ACTIVE")).strip().upper()
            status = GenericStatus.ACTIVE if status_str == "ACTIVE" else GenericStatus.INACTIVE
            
            # Root protection
            if code in ROOT_CATEGORIES:
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.FAILED, identifier=code,
                    errors=[f"Root category '{code}' is immutable and cannot be updated via import."]
                ))
                continue
                
            if not name:
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.FAILED, identifier=code,
                    errors=["Missing required field 'Category Name'"]
                ))
                continue
                
            # Verify Parent Category exists (DB or already created earlier in this batch)
            parent_id = None
            if parent_code:
                parent_cat = existing_cats.get(parent_code)
                if not parent_cat:
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=row_num, action=ImportAction.FAILED, identifier=code,
                        errors=[f"Parent category code '{parent_code}' not found. Ensure parent rows appear before child rows in the import file."]
                    ))
                    continue
                parent_id = parent_cat.id if hasattr(parent_cat, 'id') else None

                # ── FG Scope Guard ────────────────────────────────────────────────
                # Walk up the ancestor chain to check if this category descends from FG.
                # The RM sub-engine must never create children of the FG taxonomy.
                try:
                    resolver = CategoryOwnershipResolver(self.session)
                    resolved = await resolver.resolve(parent_code, memory_cache=existing_cats)
                    if resolved["domain"] == "FINISHED_GOODS":
                        result.failed_count += 1
                        result.row_results.append(ImportRowResult(
                            row_index=row_num, action=ImportAction.FAILED, identifier=code,
                            errors=[
                                f"Category '{code}' resolves to the Finished Goods taxonomy "
                                f"(ancestor 'FG'). Finished Goods categories are managed "
                                f"by the SKU Master Data Sub-Engine, not the Raw Material importer."
                            ]
                        ))
                        continue
                except ValueError as e:
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=row_num, action=ImportAction.FAILED, identifier=code,
                        errors=[str(e)]
                    ))
                    continue

            existing = existing_cats.get(code)
            
            if not existing:
                new_cat = CategoryModel(
                    id=uuid.uuid4(),
                    category_code=code,
                    category_name=name,
                    description=desc,
                    parent_id=parent_id,
                    status=status
                )
                if not is_dry_run:
                    self.session.add(new_cat)
                # Register in memory regardless of dry-run so same-batch children can resolve this parent
                existing_cats[code] = new_cat
                result.created_count += 1
                result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.CREATED, identifier=code))
            else:
                # Cannot change parent
                if existing.parent_id != parent_id:
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=row_num, action=ImportAction.FAILED, identifier=code,
                        errors=["Cannot change parent category for an existing category."]
                    ))
                    continue
                
                is_exact = (
                    existing.category_name == name and
                    (existing.description or "") == desc and
                    existing.status == status
                )
                
                if is_exact:
                    result.ignored_count += 1
                    result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.IGNORED, identifier=code))
                else:
                    if not is_dry_run:
                        existing.category_name = name
                        existing.description = desc
                        existing.status = status
                    result.updated_count += 1
                    result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.UPDATED, identifier=code))
                    
        if not is_dry_run:
            await self.session.flush()
            
        return result
