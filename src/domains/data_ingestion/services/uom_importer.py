import uuid
from typing import List, Dict, Any
from sqlalchemy import select
from src.foundation.enums.status import GenericStatus
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.data_ingestion.services.master_data_importer import (
    BaseMasterDataImporter, ImportResult, ImportRowResult, ImportAction
)

class UOMImporter(BaseMasterDataImporter):
    
    async def import_data(self, data: List[Dict[str, Any]], is_dry_run: bool = True) -> ImportResult:
        result = ImportResult(entity_type="UOM", total_records=len(data))
        
        # Pre-fetch all existing UOMs
        stmt = select(UnitOfMeasureModel)
        existing_uoms_list = (await self.session.execute(stmt)).scalars().all()
        existing_uoms = {u.unit_code: u for u in existing_uoms_list}
        
        for idx, row in enumerate(data):
            row_num = idx + 1 # 1-based for humans
            code = row.get("UoM Code")
            if not code:
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.FAILED, 
                    errors=["Missing required field 'UoM Code'"]
                ))
                continue
            
            code = str(code).strip()
            name = str(row.get("UoM Name", "")).strip()
            short_name = str(row.get("Short Name", "")).strip()
            desc = str(row.get("Description", "")).strip()
            uom_type = str(row.get("Type", "INTEGER")).strip().upper()
            status_str = str(row.get("Status", "ACTIVE")).strip().upper()
            
            status = GenericStatus.ACTIVE if status_str == "ACTIVE" else GenericStatus.INACTIVE
            
            if not name or not short_name:
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.FAILED, identifier=code,
                    errors=["Missing required fields 'UoM Name' or 'Short Name'"]
                ))
                continue
            
            existing = existing_uoms.get(code)
            
            if not existing:
                if not is_dry_run:
                    new_uom = UnitOfMeasureModel(
                        id=uuid.uuid4(),
                        unit_code=code,
                        unit_name=name,
                        short_name=short_name,
                        description=desc,
                        unit_type=uom_type,
                        status=status
                    )
                    self.session.add(new_uom)
                    existing_uoms[code] = new_uom
                result.created_count += 1
                result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.CREATED, identifier=code))
            else:
                # CERT-005: unit_type is immutable — reject if change is attempted
                if existing.unit_type != uom_type:
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=row_num, action=ImportAction.FAILED, identifier=code,
                        errors=[f"unit_type is immutable. Existing: '{existing.unit_type}', Attempted: '{uom_type}'."]
                    ))
                    continue

                # Check for exact match vs partial match
                is_exact_match = (
                    existing.unit_name == name and
                    existing.short_name == short_name and
                    (existing.description or "") == desc and
                    existing.status == status
                )
                
                if is_exact_match:
                    result.ignored_count += 1
                    result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.IGNORED, identifier=code))
                else:
                    if not is_dry_run:
                        existing.unit_name = name
                        existing.short_name = short_name
                        existing.description = desc
                        existing.status = status
                        # unit_type is NOT updated (immutable, enforced above)
                    result.updated_count += 1
                    result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.UPDATED, identifier=code))
                    
        if not is_dry_run:
            await self.session.flush()
            
        return result
