import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from tests.data_import.test_golden_migration import _run_full_init

from src.domains.data_ingestion.services.master_data_exporter import MasterDataExporter
from src.domains.data_ingestion.services.uom_importer import UOMImporter
from src.domains.data_ingestion.services.category_importer import CategoryImporter
from src.domains.data_ingestion.services.supplier_importer import SupplierImporter
from src.domains.data_ingestion.services.product_sku_importer import ProductSKUImporter
from src.domains.data_ingestion.services.bom_importer import BOMImporter

@pytest.mark.asyncio
async def test_cert021_roundtrip_certification(db_session: AsyncSession):
    """
    CERT-021: Export -> Import dry-run -> verify 0 CREATED, 0 UPDATED, 0 FAILED, 0 AMBIGUOUS
    """
    # 1. Populate the database with the golden dataset
    await _run_full_init(db_session)
    
    # 2. Run export in RESTORE mode (default)
    exporter = MasterDataExporter(db_session)
    export_data = await exporter.export_all(documentation_mode=False)
    
    # 3. Run dry-run import of the exported data
    
    # UOM
    uom_res = await UOMImporter(db_session).import_data(export_data["UoM"], is_dry_run=True)
    assert uom_res.created_count == 0
    assert uom_res.updated_count == 0
    assert uom_res.failed_count == 0
    
    # Category
    cat_res = await CategoryImporter(db_session).import_data(export_data["Operational_Categories"], is_dry_run=True)
    assert cat_res.created_count == 0
    assert cat_res.updated_count == 0
    assert cat_res.failed_count == 0
    
    # Supplier
    sup_res = await SupplierImporter(db_session).import_data(export_data["Suppliers"], is_dry_run=True)
    assert sup_res.created_count == 0
    assert sup_res.updated_count == 0
    assert sup_res.failed_count == 0
    
    # Raw Materials
    rm_res = await ProductSKUImporter(db_session).import_data(export_data["Raw_Materials"], is_dry_run=True)
    assert rm_res.created_count == 0
    assert rm_res.updated_count == 0
    assert rm_res.failed_count == 0
    
    # BOM
    bom_res = await BOMImporter(db_session).import_data(export_data["BOM"], is_dry_run=True)
    assert bom_res.created_count == 0
    assert bom_res.updated_count == 0
    assert bom_res.failed_count == 0

    # Overall AMBIGUOUS is treated as FAILED, which is asserted to be 0 above.
    
    # Also verify that EVERYTHING was ignored (matches exactly)
    assert uom_res.ignored_count == len(export_data["UoM"])
    assert cat_res.ignored_count == len(export_data["Operational_Categories"])
    assert sup_res.ignored_count == len(export_data["Suppliers"])
    assert rm_res.ignored_count == len(export_data["Raw_Materials"])
    # Note: BOM component rows are merged into BOM versions in the importer result,
    # so ignored_count might be less than row count. But it should be > 0.
    assert bom_res.ignored_count > 0
