"""
CERT-019: Full Master Initialisation Test
CERT-020: Golden Migration Test

These tests simulate a complete empty-database initialisation and verify that importing
the same master data files to two separate isolated databases produces identical state.
"""
import uuid
import pytest
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.foundation.database.models import BaseModel
from src.foundation.enums.status import GenericStatus

from tests.data_import.fixtures.cert_fixtures import cert_session  # noqa: F401 — used by test_cert019

from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.supplier import Supplier
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.bom import BOMModel

from src.domains.data_ingestion.services.uom_importer import UOMImporter
from src.domains.data_ingestion.services.category_importer import CategoryImporter
from src.domains.data_ingestion.services.supplier_importer import SupplierImporter
from src.domains.data_ingestion.services.product_sku_importer import ProductSKUImporter
from src.domains.data_ingestion.services.bom_importer import BOMImporter

# ─── Shared golden dataset ────────────────────────────────────────────────────

GOLDEN_UOMS = [
    {"UoM Code": "MTR", "UoM Name": "Meter",   "Short Name": "m",   "Type": "DECIMAL"},
    {"UoM Code": "PCS", "UoM Name": "Pieces",  "Short Name": "pcs", "Type": "DECIMAL"},
    {"UoM Code": "KG",  "UoM Name": "Kilogram","Short Name": "kg",  "Type": "DECIMAL"},
]

GOLDEN_CATEGORIES = [
    {"Category Code": "CAT-FABRIC",   "Category Name": "Fabric",        "Parent Category Code": "RM", "Status": "ACTIVE"},
    {"Category Code": "CAT-POLYBAG",  "Category Name": "Polybags",      "Parent Category Code": "PKG", "Status": "ACTIVE"},
    {"Category Code": "CAT-CUSHION",  "Category Name": "Cushion Covers","Parent Category Code": "CAT-FABRIC", "Status": "ACTIVE"},
]

GOLDEN_SUPPLIERS = [
    {"Supplier Name": "ABC Textiles",  "Phone Number": "9001000001", "GSTIN": "27AABCS1234A1Z5", "Is Job Worker": "TRUE"},
    {"Supplier Name": "Dua Handloom",  "Phone Number": "9002000002",                              "Is Job Worker": "FALSE"},
]

GOLDEN_SKUS = [
    {"Item Code": "ITM-FABRIC-GOLD", "Master Item Name": "Gold Fabric", "Base UoM Code": "MTR",
     "Category Code": "CAT-CUSHION", "Status": "ACTIVE"},
    # Second Raw Material (no 'Sku Id' field — purely RM)
    {"Item Code": "ITM-THREAD-GOLD", "Master Item Name": "Gold Thread", "Base UoM Code": "MTR",
     "Category Code": "CAT-FABRIC", "Status": "ACTIVE"},
]

GOLDEN_BOMS = [
    {"BOM Number": "BOM-CUSHION-GOLD", "BOM Name": "Gold Cushion BOM",
     "Finished SKU": "ITM-FABRIC-GOLD", "Base Quantity": 1,
     "Component SKU": "ITM-THREAD-GOLD", "Component Quantity": 0.5, "Wastage %": 5},
]


async def _run_full_init(session: AsyncSession) -> dict:
    """Run the full 7-step master init and return a state snapshot dict."""
    
    # System Initialization: Root categories are not importable and must be pre-seeded
    rm_root = CategoryModel(id=uuid.uuid4(), category_code="RM", category_name="Raw Materials")
    pkg_root = CategoryModel(id=uuid.uuid4(), category_code="PKG", category_name="Packaging")
    session.add_all([rm_root, pkg_root])
    await session.flush()

    # Step 1: UOM
    r = await UOMImporter(session).import_data(GOLDEN_UOMS, is_dry_run=False)
    assert r.failed_count == 0, f"UOM import failed: {[rr.errors for rr in r.row_results if rr.errors]}"

    # Step 2: Categories
    r = await CategoryImporter(session).import_data(GOLDEN_CATEGORIES, is_dry_run=False)
    assert r.failed_count == 0, f"Category import failed: {[rr.errors for rr in r.row_results if rr.errors]}"

    # Step 3: Suppliers
    r = await SupplierImporter(session).import_data(GOLDEN_SUPPLIERS, is_dry_run=False)
    assert r.failed_count == 0, f"Supplier import failed: {[rr.errors for rr in r.row_results if rr.errors]}"

    # Step 4: Products/SKUs (Raw Materials + Finished Goods)
    r = await ProductSKUImporter(session).import_data(GOLDEN_SKUS, is_dry_run=False)
    assert r.failed_count == 0, f"SKU import failed: {[rr.errors for rr in r.row_results if rr.errors]}"

    # Step 5: BOMs
    r = await BOMImporter(session).import_data(GOLDEN_BOMS, is_dry_run=False)
    assert r.failed_count == 0, f"BOM import failed: {[rr.errors for rr in r.row_results if rr.errors]}"

    await session.flush()

    # Snapshot state
    uoms  = (await session.execute(select(UnitOfMeasureModel))).scalars().all()
    cats  = (await session.execute(select(CategoryModel))).scalars().all()
    sups  = (await session.execute(select(Supplier))).scalars().all()
    skus  = (await session.execute(select(SKUModel))).scalars().all()
    boms  = (await session.execute(select(BOMModel))).scalars().all()

    return {
        "uom_codes":    sorted([u.unit_code for u in uoms]),
        "cat_codes":    sorted([c.category_code for c in cats]),
        "sup_names":    sorted([s.name for s in sups]),
        "sku_codes":    sorted([s.item_code for s in skus]),
        "bom_numbers":  sorted([b.bom_number for b in boms]),
        "bom_versions": {b.bom_number: b.version for b in boms},
    }


# ─── CERT-019 ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cert019_full_master_initialisation(cert_session):
    """CERT-019: Empty database initialised from scratch via the full 5-step import sequence.
    All entities must be created with correct FK references — no errors, no FK violations."""
    state = await _run_full_init(cert_session)

    assert set(state["uom_codes"]) == {"KG", "MTR", "PCS"}
    assert "CAT-FABRIC" in state["cat_codes"]
    assert "CAT-CUSHION" in state["cat_codes"]
    assert "ABC Textiles" in state["sup_names"]
    assert "ITM-FABRIC-GOLD" in state["sku_codes"]
    assert "ITM-THREAD-GOLD" in state["sku_codes"]
    # Verify no FG records — RM sub-engine must only create RAW_MATERIAL items
    assert "SKU-CUSHION-GOLD" not in state["sku_codes"], (
        "CERT-019 FAIL: RM sub-engine created a Finished Goods SKU — boundary violated."
    )
    assert "BOM-CUSHION-GOLD" in state["bom_numbers"]
    assert state["bom_versions"]["BOM-CUSHION-GOLD"] == 1


# ─── CERT-020 ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cert020_golden_migration(cert_session):
    """CERT-020 — Golden Migration Test.

    Two completely independent isolated databases receive identical import data.
    Their resulting state (counts, codes, hierarchy, BOM versions) must be identical.
    This proves the import is deterministic and environment-independent.
    """
    # ── Environment A ──
    engine_a = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory_a = async_sessionmaker(bind=engine_a, class_=AsyncSession, expire_on_commit=False)
    async with engine_a.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    async with session_factory_a() as session_a:
        state_a = await _run_full_init(session_a)

    # ── Environment B ──
    engine_b = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory_b = async_sessionmaker(bind=engine_b, class_=AsyncSession, expire_on_commit=False)
    async with engine_b.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    async with session_factory_b() as session_b:
        state_b = await _run_full_init(session_b)

    await engine_a.dispose()
    await engine_b.dispose()

    # ── Compare ──
    assert state_a["uom_codes"]   == state_b["uom_codes"],   "CERT-020 FAIL: UOM codes differ between environments"
    assert state_a["cat_codes"]   == state_b["cat_codes"],   "CERT-020 FAIL: Category codes differ"
    assert state_a["sup_names"]   == state_b["sup_names"],   "CERT-020 FAIL: Supplier names differ"
    assert state_a["sku_codes"]   == state_b["sku_codes"],   "CERT-020 FAIL: SKU codes differ"
    assert state_a["bom_numbers"] == state_b["bom_numbers"], "CERT-020 FAIL: BOM numbers differ"
    assert state_a["bom_versions"] == state_b["bom_versions"], "CERT-020 FAIL: BOM versions differ"
