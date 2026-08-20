"""
CERT-012: BOM Exact Content Match → IGNORE
CERT-013: BOM Content Change → New Version
CERT-014: BOM Duplicate Component Handling
CERT-015: Dependency Order — BOM requires SKUs to exist first
"""
import uuid
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from tests.data_import.fixtures.cert_fixtures import cert_session, seed_sku
from src.domains.masters.models.bom import BOMModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.domains.data_ingestion.services.bom_importer import BOMImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction


@pytest.fixture
async def bom_skus(cert_session):
    """Seed the target FG SKU and one component Raw Material SKU."""
    target = await seed_sku(cert_session, "SKU-BED-KING", sku_code="SKU-BED-KING")
    comp1 = await seed_sku(cert_session, "ITM-FABRIC-A", sku_code="ITM-FABRIC-A")
    comp2 = await seed_sku(cert_session, "ITM-THREAD",   sku_code="ITM-THREAD")
    return target, comp1, comp2


@pytest.mark.asyncio
async def test_cert012_bom_exact_content_match(cert_session, bom_skus):
    """CERT-012: Importing an identical BOM a second time (even with different version number) must IGNORE."""
    importer = BOMImporter(cert_session)
    data = [
        {"BOM Number": "BOM-KING", "BOM Name": "King BOM", "Finished SKU": "SKU-BED-KING",
         "Base Quantity": 1, "Component SKU": "ITM-FABRIC-A", "Component Quantity": 2.875, "Wastage %": 0, "Version": 1},
        {"BOM Number": "BOM-KING", "BOM Name": "King BOM", "Finished SKU": "SKU-BED-KING",
         "Base Quantity": 1, "Component SKU": "ITM-THREAD",   "Component Quantity": 0.05,  "Wastage %": 0, "Version": 1},
    ]

    r1 = await importer.import_data(data, is_dry_run=False)
    assert r1.created_count == 2

    # Second import — exactly the same content but "Version": 2 in file → must still IGNORE
    data[0]["Version"] = 2
    data[1]["Version"] = 2
    r2 = await importer.import_data(data, is_dry_run=False)
    assert r2.ignored_count == 2, "CERT-012 FAIL: Identical BOM created a duplicate version"
    assert r2.created_count == 0

    # Only one BOM in DB
    boms = (await cert_session.execute(select(BOMModel).where(BOMModel.bom_number == "BOM-KING"))).scalars().all()
    assert len(boms) == 1


@pytest.mark.asyncio
async def test_cert013_bom_content_change_creates_new_version(cert_session, bom_skus):
    """CERT-013: Changing a component quantity must archive old BOM and create a new active version."""
    importer = BOMImporter(cert_session)
    base_data = [
        {"BOM Number": "BOM-KING", "BOM Name": "King BOM", "Finished SKU": "SKU-BED-KING",
         "Base Quantity": 1, "Component SKU": "ITM-FABRIC-A", "Component Quantity": 2.875, "Wastage %": 0},
    ]

    r1 = await importer.import_data(base_data, is_dry_run=False)
    assert r1.created_count == 1

    # Change component quantity
    base_data[0]["Component Quantity"] = 3.000
    r2 = await importer.import_data(base_data, is_dry_run=False)
    assert r2.created_count == 1, "CERT-013 FAIL: New version not created for changed content"

    boms = (await cert_session.execute(
        select(BOMModel).options(selectinload(BOMModel.items))
        .where(BOMModel.bom_number == "BOM-KING")
        .order_by(BOMModel.version)
    )).scalars().all()

    assert len(boms) == 2, "CERT-013 FAIL: Expected 2 BOM versions"
    assert boms[0].status == "ARCHIVED", "CERT-013 FAIL: Old version not archived"
    assert boms[1].status == "ACTIVE",   "CERT-013 FAIL: New version not active"
    assert boms[1].version == 2,          "CERT-013 FAIL: Version not incremented"
    assert float(boms[1].items[0].quantity) == 3.0


@pytest.mark.asyncio
async def test_cert014_bom_duplicate_component_in_file(cert_session, bom_skus):
    """CERT-014: Exact duplicate component lines in the import file are silently deduplicated at app layer."""
    importer = BOMImporter(cert_session)
    data = [
        {"BOM Number": "BOM-DEDUP", "Finished SKU": "SKU-BED-KING",
         "Base Quantity": 1, "Component SKU": "ITM-FABRIC-A", "Component Quantity": 2.0, "Wastage %": 0},
        # Exact duplicate of above — same SKU, same qty
        {"BOM Number": "BOM-DEDUP", "Finished SKU": "SKU-BED-KING",
         "Base Quantity": 1, "Component SKU": "ITM-FABRIC-A", "Component Quantity": 2.0, "Wastage %": 0},
    ]

    r = await importer.import_data(data, is_dry_run=False)
    # One created, one ignored (duplicate line in file)
    assert r.failed_count == 0, "CERT-014 FAIL: Duplicate component raised an error"

    bom = (await cert_session.execute(
        select(BOMModel).options(selectinload(BOMModel.items)).where(BOMModel.bom_number == "BOM-DEDUP")
    )).scalars().first()
    assert len(bom.items) == 1, "CERT-014 FAIL: Duplicate component line was stored in DB"


@pytest.mark.asyncio
async def test_cert015_dependency_order_bom_requires_sku(cert_session):
    """CERT-015: Importing a BOM whose target SKU does not exist must fail with a clear dependency error."""
    importer = BOMImporter(cert_session)
    data = [
        {"BOM Number": "BOM-GHOST", "Finished SKU": "SKU-DOES-NOT-EXIST",
         "Base Quantity": 1, "Component SKU": "ITM-FABRIC-A", "Component Quantity": 2.0, "Wastage %": 0},
    ]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.failed_count >= 1, "CERT-015 FAIL: Missing SKU dependency not detected"
    assert "not found" in r.row_results[0].errors[0]

    boms = (await cert_session.execute(select(BOMModel).where(BOMModel.bom_number == "BOM-GHOST"))).scalars().all()
    assert len(boms) == 0, "CERT-015 FAIL: BOM was created despite missing dependency"
