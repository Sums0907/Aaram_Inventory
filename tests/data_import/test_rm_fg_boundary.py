"""
Phase 1 Boundary Tests — Raw Material Sub-Engine must NOT handle Finished Goods.

These tests are written BEFORE the production code is changed.
They define the expected post-refactor behaviour and will FAIL until Phase 2-3 are implemented.

Tests marked with xfail_until_refactor will be removed from xfail once the refactor lands.
"""
import pytest
from tests.data_import.fixtures.cert_fixtures import cert_session, seed_category
from src.domains.data_ingestion.services.product_sku_importer import ProductSKUImporter
from src.domains.data_ingestion.services.category_importer import CategoryImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction
from src.foundation.enums import ItemType
from sqlalchemy import select
from src.domains.masters.models.product import ProductModel


# ─── ProductSKUImporter boundary tests ────────────────────────────────────────

@pytest.mark.asyncio
async def test_rm_importer_rejects_fg_sku_id_field(cert_session):
    """
    BOUNDARY-001: Raw Material importer must reject any row that contains a
    non-empty 'Sku Id' field, which is the ShopDeck Finished Goods identifier.

    Expected after refactor: FAILED with 'Finished Goods SKUs are managed by
    the SKU Master Data Sub-Engine'.
    Currently (pre-refactor): Silently creates a FINISHED_GOODS record — WRONG behaviour.
    This test defines the TARGET behaviour post-refactor.
    """
    importer = ProductSKUImporter(cert_session)
    # Row contains 'Sku Id' — the ShopDeck FG identifier
    data = [{"Item Code": "AH-FRLK-KDB-5PC", "Sku Id": "AH-FRLK-KDB-5PC",
             "Master Item Name": "Frills Bedsheet", "Status": "ACTIVE"}]

    r = await importer.import_data(data, is_dry_run=False)

    # TARGET: must FAIL with clear FG boundary message
    assert r.failed_count == 1, (
        "BOUNDARY-001 FAIL: RM importer accepted a Finished Goods row (Sku Id present). "
        "This row must be rejected — FG SKUs belong to SKU Master Data Sub-Engine."
    )
    assert "Sub-Engine" in r.row_results[0].errors[0] or "Finished Goods" in r.row_results[0].errors[0], (
        "BOUNDARY-001 FAIL: Error message must mention Finished Goods / Sub-Engine boundary."
    )

    # No FINISHED_GOODS record must be created
    prods = (await cert_session.execute(select(ProductModel))).scalars().all()
    fg_prods = [p for p in prods if p.item_type == ItemType.FINISHED_GOODS]
    assert len(fg_prods) == 0, (
        "BOUNDARY-001 FAIL: RM importer created a FINISHED_GOODS product record — this is forbidden."
    )


@pytest.mark.asyncio
async def test_rm_importer_accepts_raw_material_without_sku_id(cert_session):
    """
    BOUNDARY-002: Raw Material importer must accept rows WITHOUT 'Sku Id' field
    and must always create RAW_MATERIAL item_type records.
    This test must PASS both before and after refactor.
    """
    importer = ProductSKUImporter(cert_session)
    data = [{"Item Code": "ITM-FABRIC-01", "Master Item Name": "Cotton Fabric",
             "Status": "ACTIVE"}]

    r = await importer.import_data(data, is_dry_run=False)
    assert r.failed_count == 0, f"BOUNDARY-002 FAIL: Valid RM row was rejected: {[rr.errors for rr in r.row_results if rr.errors]}"
    assert r.created_count == 1

    prod = (await cert_session.execute(
        select(ProductModel).where(ProductModel.product_code == "ITM-FABRIC-01")
    )).scalars().first()
    assert prod is not None
    assert prod.item_type == ItemType.RAW_MATERIAL, (
        f"BOUNDARY-002 FAIL: Expected RAW_MATERIAL, got {prod.item_type}"
    )


@pytest.mark.asyncio
async def test_rm_importer_rejects_fg_sku_id_even_in_dry_run(cert_session):
    """
    BOUNDARY-003: FG rejection must happen in dry-run mode too — it is a
    validation error, not a DB write error.
    """
    importer = ProductSKUImporter(cert_session)
    data = [{"Item Code": "AH-FG-01", "Sku Id": "AH-FG-01",
             "Master Item Name": "Finished Goods Item", "Status": "ACTIVE"}]

    r = await importer.import_data(data, is_dry_run=True)
    assert r.failed_count == 1, "BOUNDARY-003 FAIL: FG row not rejected in dry-run mode"


# ─── CategoryImporter boundary tests ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_operational_category_importer_rejects_fg_child(cert_session):
    """
    BOUNDARY-004: OperationalCategoryImporter must reject any category whose
    parent_code resolves to the 'FG' root (or any FG descendant).

    Expected after refactor: FAILED with FG scope guard message.
    Currently (pre-refactor): Allows creation — WRONG behaviour.
    """
    # Seed the FG root (simulate it existing in DB — normally immutable)
    from src.domains.masters.models.category import CategoryModel
    from src.foundation.enums.status import GenericStatus
    import uuid
    fg_root = CategoryModel(
        id=uuid.uuid4(), category_code="FG",
        category_name="Finished Goods", status=GenericStatus.ACTIVE
    )
    cert_session.add(fg_root)
    await cert_session.flush()

    importer = CategoryImporter(cert_session)
    data = [{"Category Code": "FG-BEDSHEET", "Category Name": "Bedsheets",
             "Parent Category Code": "FG", "Status": "ACTIVE"}]

    r = await importer.import_data(data, is_dry_run=False)

    # TARGET: must FAIL with FG scope guard message
    assert r.failed_count == 1, (
        "BOUNDARY-004 FAIL: RM category importer accepted an FG child category. "
        "Finished Goods categories must be rejected by OperationalCategoryImporter."
    )
    assert "Finished Goods" in r.row_results[0].errors[0] or "Sub-Engine" in r.row_results[0].errors[0], (
        "BOUNDARY-004 FAIL: Error must mention Finished Goods / Sub-Engine."
    )


@pytest.mark.asyncio
async def test_operational_category_importer_accepts_rm_child(cert_session):
    """
    BOUNDARY-005: OperationalCategoryImporter must accept categories under RM root.
    This test must PASS both before and after refactor.
    """
    rm_root = await seed_category(cert_session, "RM", "Raw Materials")

    importer = CategoryImporter(cert_session)
    data = [{"Category Code": "RM-FABRIC", "Category Name": "Fabrics",
             "Parent Category Code": "RM", "Status": "ACTIVE"}]

    # Note: RM is a root category — protected from IMPORT (cannot be in import file itself).
    # But a CHILD of RM must be accepted.
    r = await importer.import_data(data, is_dry_run=False)
    assert r.failed_count == 0, (
        f"BOUNDARY-005 FAIL: Valid RM child rejected: {[rr.errors for rr in r.row_results if rr.errors]}"
    )
    assert r.created_count == 1
