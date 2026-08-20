from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.data_ingestion.services.exporters.uom_exporter import UOMExporter
from src.domains.data_ingestion.services.exporters.category_exporter import CategoryExporter
from src.domains.data_ingestion.services.exporters.supplier_exporter import SupplierExporter
from src.domains.data_ingestion.services.exporters.raw_material_exporter import RawMaterialExporter
from src.domains.data_ingestion.services.exporters.bom_exporter import BOMExporter

class MasterDataExporter:
    """
    Coordinates entity-level exporters to produce a complete Raw Material export payload.
    Provides metadata for format versioning and round-trip safety.
    """
    
    EXPORT_FORMAT_VERSION = "RM_MASTER_EXPORT_V1"
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_all(self, documentation_mode: bool = False, include_archived_boms: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Exports all master data entities.
        If documentation_mode is True, exports all root categories (fails on re-import).
        """
        uom_data = await UOMExporter(self.session).export_data()
        category_data = await CategoryExporter(self.session).export_data(documentation_mode=documentation_mode)
        supplier_data = await SupplierExporter(self.session).export_data()
        rm_data = await RawMaterialExporter(self.session).export_data()
        bom_data = await BOMExporter(self.session).export_data(include_archived=include_archived_boms)
        
        # Calculate BOM counts from rows (one BOM has multiple rows)
        active_boms = set()
        archived_boms = set()
        for row in bom_data:
            if row["BOM Status"] == "ACTIVE":
                active_boms.add(row["BOM Number"])
            else:
                archived_boms.add(row["BOM Number"])
        
        metadata = [{
            "Export Format Version": self.EXPORT_FORMAT_VERSION,
            "Export Date": datetime.utcnow().isoformat(),
            "Environment": "Production", # TODO: Get from env config if needed
            "Exported By": "System",
            "AaramBooks Version": "0.2.0",
            "UOM Count": len(uom_data),
            "Category Count": len(category_data),
            "Supplier Count": len(supplier_data),
            "Raw Material Count": len(rm_data),
            "Active BOM Count": len(active_boms),
            "Archived BOM Count": len(archived_boms) if include_archived_boms else 0,
            "Round-Trip Safe": "FALSE" if documentation_mode else "TRUE"
        }]
        
        return {
            "UoM": uom_data,
            "Operational_Categories": category_data,
            "Suppliers": supplier_data,
            "Raw_Materials": rm_data,
            "BOM": bom_data,
            "Export_Metadata": metadata
        }
