"""
CERT-001: Exact Match Idempotency
CERT-002: Partial Match Update
CERT-005: UOM Protection (unit_type is immutable)
"""
import pytest
from sqlalchemy import select
from tests.data_import.fixtures.cert_fixtures import cert_session, seed_uom
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.data_ingestion.services.uom_importer import UOMImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction


@pytest.mark.asyncio
async def test_cert001_exact_match_idempotency(cert_session):
    """CERT-001: Running the same import twice must not create duplicates."""
    importer = UOMImporter(cert_session)
    data = [{"UoM Code": "PCS", "UoM Name": "Pieces", "Short Name": "pcs", "Type": "DECIMAL"}]

    # First run — creates
    r1 = await importer.import_data(data, is_dry_run=False)
    assert r1.created_count == 1
    assert r1.ignored_count == 0

    # Second identical run — must IGNORE, not create
    r2 = await importer.import_data(data, is_dry_run=False)
    assert r2.ignored_count == 1
    assert r2.created_count == 0

    # Verify no duplicate row in DB
    rows = (await cert_session.execute(select(UnitOfMeasureModel).where(UnitOfMeasureModel.unit_code == "PCS"))).scalars().all()
    assert len(rows) == 1, "CERT-001 FAIL: Duplicate UOM row created"


@pytest.mark.asyncio
async def test_cert002_partial_match_update(cert_session):
    """CERT-002: A partial match should update only mutable fields."""
    await seed_uom(cert_session, unit_code="MTR", unit_name="Meter", unit_type="DECIMAL")
    importer = UOMImporter(cert_session)

    data = [{"UoM Code": "MTR", "UoM Name": "Metre (updated)", "Short Name": "m", "Type": "DECIMAL"}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.updated_count == 1

    row = (await cert_session.execute(select(UnitOfMeasureModel).where(UnitOfMeasureModel.unit_code == "MTR"))).scalars().first()
    assert row.unit_name == "Metre (updated)", "CERT-002 FAIL: Name not updated"
    assert row.unit_code == "MTR", "CERT-002 FAIL: Identity code was changed"


@pytest.mark.asyncio
async def test_cert005_uom_type_immutable(cert_session):
    """CERT-005: UOM unit_type cannot be changed once created."""
    await seed_uom(cert_session, unit_code="PCS", unit_name="Pieces", unit_type="INTEGER")
    importer = UOMImporter(cert_session)

    # Try to change unit_type to DECIMAL
    data = [{"UoM Code": "PCS", "UoM Name": "Pieces", "Short Name": "pcs", "Type": "DECIMAL"}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.failed_count == 1
    assert "immutable" in r.row_results[0].errors[0].lower(), "CERT-005 FAIL: Should reject unit_type change"

    # Verify unchanged
    row = (await cert_session.execute(select(UnitOfMeasureModel).where(UnitOfMeasureModel.unit_code == "PCS"))).scalars().first()
    assert row.unit_type == "INTEGER", "CERT-005 FAIL: unit_type was mutated"
