from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel

class UOMExporter:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_data(self) -> List[Dict[str, Any]]:
        stmt = select(UnitOfMeasureModel).order_by(UnitOfMeasureModel.unit_code)
        result = await self.session.execute(stmt)
        uoms = result.scalars().all()
        
        export_rows = []
        for uom in uoms:
            export_rows.append({
                "UoM Code": uom.unit_code,
                "UoM Name": uom.unit_name,
                "Short Name": uom.short_name,
                "Type": uom.unit_type,
                "Description": uom.description or "",
                "Status": uom.status.name
            })
            
        return export_rows
