"""
CERT-001: Exact Match Idempotency (Supplier)
CERT-002: Partial Match Update (Supplier)
CERT-003: Ambiguous Match Rejection
CERT-004: Supplier Identity Protection
"""
import pytest
from sqlalchemy import select
from tests.data_import.fixtures.cert_fixtures import cert_session, seed_supplier
from src.domains.masters.models.supplier import Supplier
from src.domains.data_ingestion.services.supplier_importer import SupplierImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction


@pytest.mark.asyncio
async def test_cert001_supplier_exact_match_idempotency(cert_session):
    """CERT-001: Repeated identical supplier imports create no duplicates."""
    importer = SupplierImporter(cert_session)
    data = [{"Supplier Name": "ABC Textiles", "Phone Number": "9001000001", "GSTIN": "27AABCS1234A1Z5"}]

    r1 = await importer.import_data(data, is_dry_run=False)
    assert r1.created_count == 1

    r2 = await importer.import_data(data, is_dry_run=False)
    assert r2.ignored_count == 1
    assert r2.created_count == 0

    rows = (await cert_session.execute(select(Supplier).where(Supplier.name == "ABC Textiles"))).scalars().all()
    assert len(rows) == 1, "CERT-001 FAIL: Duplicate supplier row created"


@pytest.mark.asyncio
async def test_cert002_supplier_partial_match_update(cert_session):
    """CERT-002: Partial match updates mutable fields (address), not identity (name+GSTIN)."""
    existing = await seed_supplier(cert_session, "ABC Textiles", phone="9001000001", gstin="27AABCS1234A1Z5")
    importer = SupplierImporter(cert_session)

    data = [{"Supplier Name": "ABC Textiles", "Phone Number": "9001000001", "GSTIN": "27AABCS1234A1Z5",
             "Address": "Panipat, Haryana"}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.updated_count == 1

    row = (await cert_session.execute(select(Supplier).where(Supplier.id == existing.id))).scalars().first()
    assert row.address == "Panipat, Haryana", "CERT-002 FAIL: Address not updated"
    assert row.gstin == "27AABCS1234A1Z5", "CERT-002 FAIL: GSTIN was changed"


@pytest.mark.asyncio
async def test_cert003_ambiguous_match_rejection(cert_session):
    """CERT-003: Same phone, different name AND different GSTIN → must REJECT, not merge."""
    await seed_supplier(cert_session, "ABC Textiles", phone="9999999999", gstin="27AABCS1234A1Z5")
    importer = SupplierImporter(cert_session)

    # Completely different supplier except same phone
    data = [{"Supplier Name": "Fake Mills Co", "Phone Number": "9999999999", "GSTIN": "99FAKE9999F9Z9"}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.ambiguous_count == 1, "CERT-003 FAIL: Ambiguous match was not rejected"
    assert r.created_count == 0, "CERT-003 FAIL: Ambiguous supplier was created"

    # Verify only one supplier exists with that phone
    rows = (await cert_session.execute(select(Supplier).where(Supplier.contact_number == "9999999999"))).scalars().all()
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_cert004_supplier_identity_protection_via_id(cert_session):
    """CERT-004: Providing a non-existent Supplier ID in import must fail, not create a new record."""
    importer = SupplierImporter(cert_session)
    import uuid
    fake_id = str(uuid.uuid4())

    data = [{"Supplier ID": fake_id, "Supplier Name": "Ghost Supplier"}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.failed_count == 1, "CERT-004 FAIL: Import with non-existent Supplier ID should have failed"
    assert "not found" in r.row_results[0].errors[0]

    # No ghost supplier created
    rows = (await cert_session.execute(select(Supplier).where(Supplier.name == "Ghost Supplier"))).scalars().all()
    assert len(rows) == 0


@pytest.mark.asyncio
async def test_cert004_id_based_update_preserves_identity(cert_session):
    """CERT-004b: Update via Supplier ID updates mutable fields but preserves the UUID identity."""
    existing = await seed_supplier(cert_session, "Original Name", phone="8001000001")
    importer = SupplierImporter(cert_session)

    data = [{"Supplier ID": str(existing.id), "Supplier Name": "Updated Name"}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.updated_count == 1

    row = (await cert_session.execute(select(Supplier).where(Supplier.id == existing.id))).scalars().first()
    assert row.name == "Updated Name"
    assert row.id == existing.id, "CERT-004b FAIL: UUID identity was changed"
