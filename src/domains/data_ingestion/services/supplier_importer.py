import uuid
from typing import List, Dict, Any
from sqlalchemy import select
from src.domains.masters.models.supplier import Supplier
from src.domains.data_ingestion.services.master_data_importer import (
    BaseMasterDataImporter, ImportResult, ImportRowResult, ImportAction
)

class SupplierImporter(BaseMasterDataImporter):
    
    async def import_data(self, data: List[Dict[str, Any]], is_dry_run: bool = True) -> ImportResult:
        result = ImportResult(entity_type="SUPPLIER", total_records=len(data))
        
        # Pre-fetch all existing suppliers
        stmt = select(Supplier)
        existing_list = (await self.session.execute(stmt)).scalars().all()
        
        # Build indexes for fast lookup
        by_id = {str(s.id): s for s in existing_list}
        
        for idx, row in enumerate(data):
            row_num = idx + 1
            
            sup_id = row.get("Supplier ID")
            name = str(row.get("Supplier Name", "")).strip()
            phone = str(row.get("Phone Number", "")).strip()
            gstin = str(row.get("GSTIN", "")).strip()
            email = str(row.get("Email", "")).strip()
            address = str(row.get("Address", "")).strip()
            remarks = str(row.get("Remarks", "")).strip()
            
            is_job_worker_str = str(row.get("Is Job Worker", "FALSE")).strip().upper()
            is_job_worker = is_job_worker_str in ["TRUE", "YES", "1", "Y"]
            
            if not name:
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.FAILED,
                    errors=["Missing required field 'Supplier Name'"]
                ))
                continue
                
            existing = None
            
            # Identity Resolution
            if sup_id:
                sup_id_str = str(sup_id).strip()
                existing = by_id.get(sup_id_str)
                if not existing:
                    result.failed_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=row_num, action=ImportAction.FAILED, identifier=sup_id_str,
                        errors=[f"Provided Supplier ID '{sup_id_str}' not found in database."]
                    ))
                    continue
            else:
                # Secondary Controlled Matching
                # We need to find potential matches based on GSTIN, Name, or Phone
                matches = []
                for s in existing_list:
                    match_score = 0
                    if gstin and s.gstin == gstin:
                        match_score += 1
                    if phone and s.contact_number == phone:
                        match_score += 1
                    if name.lower() == s.name.lower():
                        match_score += 1
                        
                    if match_score > 0:
                        matches.append(s)
                        
                if len(matches) == 1:
                    # Single candidate. Ensure it's not ambiguous.
                    cand = matches[0]
                    # If it matched on phone but name is completely different and GSTIN differs...
                    # We'll allow it if at least the name is similar or they share a GSTIN.
                    # As a strict rule: if phone matches but GSTIN is different AND name is different, it's ambiguous.
                    is_ambiguous = False
                    if phone and cand.contact_number == phone:
                        name_match = (name.lower() == cand.name.lower())
                        gstin_match = (gstin and cand.gstin == gstin)
                        if not name_match and not gstin_match:
                            is_ambiguous = True
                            
                    if is_ambiguous:
                        result.ambiguous_count += 1
                        result.row_results.append(ImportRowResult(
                            row_index=row_num, action=ImportAction.AMBIGUOUS, identifier=name,
                            errors=["Ambiguous match: Phone number matches but Name and GSTIN completely differ."]
                        ))
                        continue
                    else:
                        existing = cand
                elif len(matches) > 1:
                    result.ambiguous_count += 1
                    result.row_results.append(ImportRowResult(
                        row_index=row_num, action=ImportAction.AMBIGUOUS, identifier=name,
                        errors=["Ambiguous match: Multiple existing suppliers match the provided criteria."]
                    ))
                    continue
            
            if not existing:
                if not is_dry_run:
                    new_sup = Supplier(
                        id=uuid.uuid4(),
                        name=name,
                        contact_number=phone if phone else None,
                        gstin=gstin if gstin else None,
                        email=email if email else None,
                        address=address if address else None,
                        remarks=remarks if remarks else None,
                        is_job_worker=is_job_worker
                    )
                    self.session.add(new_sup)
                    existing_list.append(new_sup)
                result.created_count += 1
                result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.CREATED, identifier=name))
            else:
                # Check for exact match
                is_exact = (
                    existing.name == name and
                    (existing.contact_number or "") == phone and
                    (existing.gstin or "") == gstin and
                    (existing.email or "") == email and
                    (existing.address or "") == address and
                    (existing.remarks or "") == remarks and
                    existing.is_job_worker == is_job_worker
                )
                
                if is_exact:
                    result.ignored_count += 1
                    result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.IGNORED, identifier=name))
                else:
                    if not is_dry_run:
                        existing.name = name
                        existing.contact_number = phone if phone else None
                        existing.gstin = gstin if gstin else None
                        existing.email = email if email else None
                        existing.address = address if address else None
                        existing.remarks = remarks if remarks else None
                        # Protected field: is_job_worker should not be changed via import once created?
                        # Wait, the rule matrix says: "Protected Fields: Is Job Worker (requires operational validation)."
                        # So we don't update it.
                        
                    result.updated_count += 1
                    result.row_results.append(ImportRowResult(row_index=row_num, action=ImportAction.UPDATED, identifier=name))
                    
        if not is_dry_run:
            await self.session.flush()
            
        return result
