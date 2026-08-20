from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.foundation.enums.status import GenericStatus
from src.domains.masters.models.bom import BOMModel

class BOMExporter:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_data(self, include_archived: bool = False) -> List[Dict[str, Any]]:
        # Export BOMs
        stmt = select(BOMModel).options(
            selectinload(BOMModel.target_item),
            selectinload(BOMModel.items).selectinload(BOMModel.items.prop.mapper.class_.component_item),
            selectinload(BOMModel.items).selectinload(BOMModel.items.prop.mapper.class_.uom)
        )
        
        if not include_archived:
            stmt = stmt.where(BOMModel.status == "ACTIVE")
            
        stmt = stmt.order_by(BOMModel.bom_number, BOMModel.version.desc())
        
        result = await self.session.execute(stmt)
        boms = result.scalars().unique().all()
        
        export_rows = []
        for bom in boms:
            for item in bom.items:
                export_rows.append({
                    "BOM Number": bom.bom_number,
                    "BOM Name": bom.bom_name or "",
                    "Finished SKU": bom.target_item.item_code if bom.target_item else "",
                    "Base Quantity": int(bom.target_quantity),
                    "Version": bom.version,
                    "BOM Status": bom.status.name if hasattr(bom.status, 'name') else str(bom.status),
                    "Effective From": bom.effective_from.isoformat() if bom.effective_from else "",
                    "Effective To": bom.effective_to.isoformat() if bom.effective_to else "",
                    
                    "Component SKU": item.component_item.item_code if item.component_item else "",
                    "Component Quantity": float(item.quantity),
                    "Wastage %": float(item.wastage_percentage) if item.wastage_percentage else 0.0,
                    "Tolerance %": float(item.tolerance_percentage) if item.tolerance_percentage else 0.0,
                    "Component UOM": item.uom.unit_code if item.uom else ""
                })
                
        return export_rows
