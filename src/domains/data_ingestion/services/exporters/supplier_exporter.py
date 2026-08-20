from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.masters.models.supplier import Supplier

class SupplierExporter:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_data(self) -> List[Dict[str, Any]]:
        stmt = select(Supplier).order_by(Supplier.name)
        result = await self.session.execute(stmt)
        suppliers = result.scalars().all()
        
        export_rows = []
        for supplier in suppliers:
            export_rows.append({
                "Supplier ID": str(supplier.id),
                "Supplier Name": supplier.name,
                "Phone Number": supplier.contact_number or "",
                "GSTIN": supplier.gstin or "",
                "Email": supplier.email or "",
                "Address": supplier.address or "",
                "Remarks": supplier.remarks or "",
                "Is Job Worker": "TRUE" if supplier.is_job_worker else "FALSE"
            })
            
        return export_rows
