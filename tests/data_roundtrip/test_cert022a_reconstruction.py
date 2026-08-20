import pytest
import uuid
from sqlalchemy import select
from tests.data_import.fixtures.cert_fixtures import cert_session
from tests.data_roundtrip.utils import import_from_excel, seed_fg_references
from src.domains.data_ingestion.services.master_data_exporter import MasterDataExporter
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.supplier import Supplier
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.bom import BOMModel

async def seed_roots(session):
    rm_root = CategoryModel(id=uuid.uuid4(), category_code="RM", category_name="Raw Materials")
    pkg_root = CategoryModel(id=uuid.uuid4(), category_code="PKG", category_name="Packaging")
    fg_root = CategoryModel(id=uuid.uuid4(), category_code="FG", category_name="Finished Goods")
    con_root = CategoryModel(id=uuid.uuid4(), category_code="CON", category_name="Consumables")
    ast_root = CategoryModel(id=uuid.uuid4(), category_code="AST", category_name="Assets")
    session.add_all([rm_root, pkg_root, fg_root, con_root, ast_root])
    await session.flush()

@pytest.mark.asyncio
async def test_cert022a_reconstruction(cert_session):
    """CERT-022A: RM Master Reconstruction"""
    await seed_roots(cert_session)
    await seed_fg_references(cert_session)
    
    # 1. Import
    import_path = "tests/data/RM_MASTER_CERTIFICATION_DATA.xlsx"
    results = await import_from_excel(import_path, cert_session)
    
    # Assert nothing failed entirely
    for domain, res in results.items():
        assert res.failed_count == 0, f"Import failed for {domain}: {[rr.errors for rr in res.row_results if rr.errors]}"
        
    await cert_session.flush()
    
    # Validate DB A state
    uoms = (await cert_session.execute(select(UnitOfMeasureModel))).scalars().all()
    assert len(uoms) > 0, "No UOMs imported"
    
    skus = (await cert_session.execute(select(SKUModel))).scalars().all()
    assert len(skus) > 0, "No SKUs imported"
    
    # 2. Export
    exporter = MasterDataExporter(cert_session)
    export_data = await exporter.export_all()
    
    assert len(export_data["UoM"]) == len(uoms)
    assert len(export_data["Suppliers"]) > 0
    assert len(export_data["Raw_Materials"]) > 0
    assert len(export_data["BOM"]) > 0

