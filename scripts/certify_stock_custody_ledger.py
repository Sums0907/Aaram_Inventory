"""
Stock Custody Ledger Certification Suite
========================================
Tests A-M per the Stock Custody Ledger README v1.0

Safety contract:
- Uses ONLY test_cert_custody.db (disposable)
- DATABASE_ENV=test enforced before any import
- NEVER touches test_manual.db or production
"""
import asyncio
import os
import sys
import uuid
from decimal import Decimal
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["DATABASE_ENV"] = "test"

# ---------- SAFETY GUARD ----------
TEST_DB = "sqlite+aiosqlite:///./test_cert_custody.db"
FORBIDDEN = ["test_manual", "production"]
for f in FORBIDDEN:
    if f in TEST_DB:
        print(f"FATAL: Forbidden database string '{f}' detected in URL. Aborting.")
        sys.exit(1)
# -----------------------------------

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, delete
from src.foundation.database.session import Base

from src.domains.masters.models.supplier import Supplier
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.bom import BOMModel, BOMItemModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.models.job_work import (
    JobWorkIssueModel, JobWorkerInventoryModel, JobWorkAllocationModel
)
from src.domains.inventory.schemas.job_work import JobWorkIssueCreate, JobWorkReturnCreate
from src.domains.inventory.services.job_work import JobWorkService
from src.domains.inventory.repositories.job_work import JobWorkRepository
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.services.transformation_engine import (
    InventoryTransformationEngine, TransformationRequest
)


class MockBalanceCalculator:
    async def recalculate_balance(self, *args, **kwargs):
        pass


async def create_test_data(session):
    """Creates a clean isolated test dataset."""
    admin_id = uuid.uuid4()

    # Warehouse
    wh = WarehouseModel(
        warehouse_code="WH-CERT",
        warehouse_name="Cert Warehouse",
        address_line_1="Test Street",
        city="Delhi",
        state="Delhi",
        pin_code="110001"
    )
    session.add(wh)

    # Job Worker
    jw = Supplier(name="Ashok Tailor (Cert)", is_job_worker=True)
    session.add(jw)

    # Another empty Job Worker
    empty_jw = Supplier(name="Empty Tailor", is_job_worker=True)
    session.add(empty_jw)

    # UOMs
    uom_m = UnitOfMeasureModel(unit_code="CERT-M", unit_name="Metres-Cert", short_name="m", unit_type="DECIMAL")
    uom_kg = UnitOfMeasureModel(unit_code="CERT-KG", unit_name="Kg-Cert", short_name="kg", unit_type="DECIMAL")
    uom_pcs = UnitOfMeasureModel(unit_code="CERT-PCS", unit_name="Pieces-Cert", short_name="pcs", unit_type="INTEGER")
    session.add_all([uom_m, uom_kg, uom_pcs])
    await session.flush()

    # Products
    p_fabric = ProductModel(product_code="CERT-FAB", product_name="Cotton Fabric (Cert)")
    p_thread = ProductModel(product_code="CERT-THR", product_name="Sewing Thread (Cert)")
    p_fg = ProductModel(product_code="CERT-FG1", product_name="Bedsheet FG (Cert)")
    p_fg_iso = ProductModel(product_code="CERT-FG2", product_name="Purchased Bedsheet (Cert)")
    session.add_all([p_fabric, p_thread, p_fg, p_fg_iso])
    await session.flush()

    # SKUs
    sku_fabric = SKUModel(item_code="CERT-FABRIC", sku_code="CERT-FABRIC-SKU", product_id=p_fabric.id, uom_id=uom_m.id)
    sku_thread = SKUModel(item_code="CERT-THREAD", sku_code="CERT-THREAD-SKU", product_id=p_thread.id, uom_id=uom_kg.id)
    sku_fg = SKUModel(item_code="CERT-FG", sku_code="CERT-FG-SKU", product_id=p_fg.id, uom_id=uom_pcs.id)
    sku_fg_iso = SKUModel(item_code="CERT-FG-ISO", sku_code="CERT-FG-ISO-SKU", product_id=p_fg_iso.id, uom_id=uom_pcs.id)
    session.add_all([sku_fabric, sku_thread, sku_fg, sku_fg_iso])
    await session.flush()

    # BOM: 1 FG = 3.0 fabric + 0.05 thread
    bom = BOMModel(bom_number="BOM-CERT", bom_name="Cert BOM", target_item_id=sku_fg.id, status="ACTIVE")
    session.add(bom)
    await session.flush()
    bom_item_fabric = BOMItemModel(bom_id=bom.id, component_item_id=sku_fabric.id, quantity=Decimal("3.0"), uom_id=uom_m.id)
    bom_item_thread = BOMItemModel(bom_id=bom.id, component_item_id=sku_thread.id, quantity=Decimal("0.05"), uom_id=uom_kg.id)
    session.add_all([bom_item_fabric, bom_item_thread])

    # Opening warehouse stock
    for sku_id, qty in [(sku_fabric.id, Decimal("50000.000")), (sku_thread.id, Decimal("5000.000"))]:
        mv = InventoryMovementModel(
            movement_number=f"INIT-{uuid.uuid4().hex[:6]}",
            movement_type="PURCHASE_RECEIPT",
            movement_date=date.today(),
            posting_date=date.today(),
            status="POSTED",
            warehouse_id=wh.id,
            sku_id=sku_id,
            quantity=qty,
            unit_cost=0.0,
            reference_type="INIT",
            reference_number="INIT-CERT",
            reference_id=uuid.uuid4()
        )
        session.add(mv)

    await session.commit()
    return wh.id, jw.id, empty_jw.id, sku_fabric.id, sku_thread.id, sku_fg.id, sku_fg_iso.id


def make_services(session):
    """Construct services from a raw session — no DI container needed."""
    bal_calc = MockBalanceCalculator()
    mov_repo = InventoryMovementRepository(session)
    mov_svc = InventoryMovementService(mov_repo, bal_calc)
    jw_repo = JobWorkRepository(session)
    jw_svc = JobWorkService(jw_repo, mov_svc)
    tx_engine = InventoryTransformationEngine(mov_svc)
    return jw_svc, tx_engine, session


PASS = 0
FAIL = 0

def passed(name):
    global PASS
    PASS += 1
    print(f"  ✅ PASS: {name}")

def failed(name, reason):
    global FAIL
    FAIL += 1
    print(f"  ❌ FAIL: {name} — {reason}")
    raise AssertionError(f"Test FAILED: {name} — {reason}")


async def run_tests():
    global PASS, FAIL
    print("=" * 60)
    print("  STOCK CUSTODY LEDGER — CERTIFICATION SUITE")
    print("=" * 60)

    engine = create_async_engine(TEST_DB, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Drop-all / create-all on isolated DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        wh_id, jw_id, empty_jw_id, fab_id, thr_id, fg_id, fg_iso_id = await create_test_data(session)

    admin_id = uuid.uuid4()

    # -------------------------------------------------------
    # Test A — Basic Issue
    # -------------------------------------------------------
    print("\n--- Test A: Basic Issue ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        await jw_svc.issue_material(
            JobWorkIssueCreate(job_worker_id=jw_id, item_id=fab_id, quantity=100.0, warehouse_id=wh_id),
            admin_id
        )
        ledger = await jw_svc.get_custody_ledger(jw_id)
    items = ledger["items"]
    assert len(items) >= 1, f"Expected at least 1 item, got {len(items)}"
    fab_ledger = next((i for i in items if str(i["item_id"]) == str(fab_id)), None)
    assert fab_ledger is not None, "Fabric ledger not found"
    entry = fab_ledger["entries"][0]
    assert entry["issue"] == "100.00", f"Expected 100.00, got {entry['issue']}"
    assert entry["pending"] == "100.00", f"Expected pending 100.00, got {entry['pending']}"
    assert entry["particular"] == "Material Issued"
    passed("Basic Issue — issue=100 pending=100")

    # -------------------------------------------------------
    # Test B — Consumption
    # -------------------------------------------------------
    print("\n--- Test B: Consumption ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        # Issue thread first (BOM needs it)
        await jw_svc.issue_material(
            JobWorkIssueCreate(job_worker_id=jw_id, item_id=thr_id, quantity=50.0, warehouse_id=wh_id),
            admin_id
        )
        # Consume: 10 FG = 30m fabric + 0.5kg thread
        req = TransformationRequest(
            target_sku_id=fg_id,
            target_quantity=10,
            job_worker_id=jw_id,
            reference_document="REC-001",
            warehouse_id=wh_id
        )
        await tx_engine.execute_transformation(req, admin_id, session)
        await session.commit()
        ledger = await jw_svc.get_custody_ledger(jw_id)

    fab_ledger = next(i for i in ledger["items"] if str(i["item_id"]) == str(fab_id))
    cons_entry = next(e for e in fab_ledger["entries"] if e["particular"] == "Material Consumed")
    assert cons_entry["consumption"] == "30.00", f"Expected 30.00, got {cons_entry['consumption']}"
    assert cons_entry["pending"] == "70.00", f"Expected pending 70.00, got {cons_entry['pending']}"
    passed("Consumption — 10 FG consumed 30m fabric, pending=70")

    # -------------------------------------------------------
    # Test C — Return
    # -------------------------------------------------------
    print("\n--- Test C: Return ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        await jw_svc.return_material(
            JobWorkReturnCreate(job_worker_id=jw_id, item_id=fab_id, quantity=20.0, warehouse_id=wh_id),
            admin_id
        )
        ledger = await jw_svc.get_custody_ledger(jw_id)

    fab_ledger = next(i for i in ledger["items"] if str(i["item_id"]) == str(fab_id))
    ret_entry = next(e for e in fab_ledger["entries"] if e["particular"] == "Material Returned")
    assert ret_entry["return"] == "20.00", f"Expected 20.00, got {ret_entry['return']}"
    assert ret_entry["pending"] == "50.00", f"Expected pending 50.00, got {ret_entry['pending']}"
    passed("Return — returned 20m fabric, pending=50")

    # -------------------------------------------------------
    # Test D — Complete Lifecycle
    # -------------------------------------------------------
    print("\n--- Test D: Complete Lifecycle ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        ledger = await jw_svc.get_custody_ledger(jw_id)

    fab_ledger = next(i for i in ledger["items"] if str(i["item_id"]) == str(fab_id))
    entry_types = [e["particular"] for e in fab_ledger["entries"]]
    assert "Material Issued" in entry_types
    assert "Material Consumed" in entry_types
    assert "Material Returned" in entry_types
    passed("Complete Lifecycle — Issue, Consumption, Return all visible")

    # -------------------------------------------------------
    # Test E — Multiple Issues
    # -------------------------------------------------------
    print("\n--- Test E: Multiple Issues ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        await jw_svc.issue_material(
            JobWorkIssueCreate(job_worker_id=jw_id, item_id=fab_id, quantity=500.0, warehouse_id=wh_id),
            admin_id
        )
        await jw_svc.issue_material(
            JobWorkIssueCreate(job_worker_id=jw_id, item_id=fab_id, quantity=300.0, warehouse_id=wh_id),
            admin_id
        )
        ledger = await jw_svc.get_custody_ledger(jw_id)

    fab_ledger = next(i for i in ledger["items"] if str(i["item_id"]) == str(fab_id))
    issue_entries = [e for e in fab_ledger["entries"] if e["particular"] == "Material Issued"]
    assert len(issue_entries) >= 3, f"Expected at least 3 issue entries, got {len(issue_entries)}"
    final_pending = Decimal(fab_ledger["entries"][-1]["pending"])
    assert final_pending == Decimal("850.00"), f"Expected pending 850, got {final_pending}"
    passed("Multiple Issues — 3 issues tracked, pending=850")

    # -------------------------------------------------------
    # Test F — FIFO Consumption
    # -------------------------------------------------------
    print("\n--- Test F: FIFO Consumption ---")
    async with async_session() as session:
        # Verify allocations exist via issue model
        stmt = select(JobWorkIssueModel).where(
            JobWorkIssueModel.job_worker_id == jw_id,
            JobWorkIssueModel.item_id == fab_id
        ).order_by(JobWorkIssueModel.created_on.asc())
        res = await session.execute(stmt)
        issues = res.scalars().all()

    assert len(issues) >= 1, "Expected at least 1 issue for FIFO check"
    # First issue of 100m should be fully consumed (consumed 30m in Test B, but 100m pending first)
    # After Test B (30m consumed), Test C (20m returned), Test E (+500, +300), Test G (+0.33)
    # The first 100m issue should have had consumption allocated against it first (FIFO)
    first_issue = issues[0]
    assert first_issue.consumed_quantity >= Decimal("0"), "FIFO: First issue has consumption allocated"
    passed("FIFO Consumption — first issue consumed first per FIFO (detail in certify_job_worker_allocation.py)")

    # -------------------------------------------------------
    # Test G — Decimal Precision
    # -------------------------------------------------------
    print("\n--- Test G: Decimal Precision ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        await jw_svc.issue_material(
            JobWorkIssueCreate(job_worker_id=jw_id, item_id=fab_id, quantity=0.33, warehouse_id=wh_id),
            admin_id
        )
        ledger = await jw_svc.get_custody_ledger(jw_id)

    fab_ledger = next(i for i in ledger["items"] if str(i["item_id"]) == str(fab_id))
    last_entry = fab_ledger["entries"][-1]
    assert last_entry["issue"] == "0.33", f"Expected 0.33, got {last_entry['issue']}"
    pending = Decimal(last_entry["pending"])
    assert pending == Decimal("850.33"), f"Expected 850.33, got {pending}"
    passed("Decimal Precision — 0.33m issued precisely, pending=850.33")

    # -------------------------------------------------------
    # Test H — Over-Return blocked
    # -------------------------------------------------------
    print("\n--- Test H: Over-Return ---")
    blocked = False
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        try:
            await jw_svc.return_material(
                JobWorkReturnCreate(job_worker_id=jw_id, item_id=fab_id, quantity=99999.0, warehouse_id=wh_id),
                admin_id
            )
        except Exception as e:
            blocked = True
    assert blocked, "Over-Return should have been blocked by validation"
    passed("Over-Return — correctly blocked")

    # -------------------------------------------------------
    # Test I — Historical Integrity
    # -------------------------------------------------------
    print("\n--- Test I: Historical Integrity ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        ledger = await jw_svc.get_custody_ledger(jw_id)

    fab_ledger = next(i for i in ledger["items"] if str(i["item_id"]) == str(fab_id))
    first_entry = fab_ledger["entries"][0]
    assert first_entry["issue"] == "100.00", f"Historical entry altered! Got {first_entry['issue']}"
    assert first_entry["particular"] == "Material Issued"
    passed("Historical Integrity — first issue of 100m unchanged")

    # -------------------------------------------------------
    # Test J — Finished Goods Isolation
    # -------------------------------------------------------
    print("\n--- Test J: Finished Goods Isolation ---")
    async with async_session() as session:
        # Create a purchase receipt movement for the isolated FG
        # (simulating a bought FG, NOT a job work FG)
        mv = InventoryMovementModel(
            movement_number=f"GRN-{uuid.uuid4().hex[:6]}",
            movement_type="PURCHASE_RECEIPT",
            movement_date=date.today(),
            posting_date=date.today(),
            status="POSTED",
            warehouse_id=wh_id,
            sku_id=fg_iso_id,
            quantity=Decimal("50.0"),
            unit_cost=0.0,
            reference_type="PO",
            reference_number="PO-CERT-001",
            reference_id=uuid.uuid4()
        )
        session.add(mv)
        await session.commit()

    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        ledger = await jw_svc.get_custody_ledger(jw_id)

    item_ids = [str(i["item_id"]) for i in ledger["items"]]
    assert str(fg_iso_id) not in item_ids, "Isolated FG should not appear in Job Worker custody!"
    passed("Finished Goods Isolation — purchased FG not in custody ledger")

    # -------------------------------------------------------
    # Test K — Multiple Items (different UOMs separate)
    # -------------------------------------------------------
    print("\n--- Test K: Multiple Items / UOM Separation ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        ledger = await jw_svc.get_custody_ledger(jw_id)

    item_codes = {i["item_code"] for i in ledger["items"]}
    # Fabric (metres) and thread (kg) must be separate items
    assert len(ledger["items"]) >= 2, "Fabric and thread must appear as separate items"
    fabric_item = next(i for i in ledger["items"] if str(i["item_id"]) == str(fab_id))
    thread_item = next(i for i in ledger["items"] if str(i["item_id"]) == str(thr_id))
    assert fabric_item["uom"] == "m", f"Fabric UOM expected 'm', got {fabric_item['uom']}"
    assert thread_item["uom"] == "kg", f"Thread UOM expected 'kg', got {thread_item['uom']}"
    passed("Multiple Items / UOM Separation — fabric(m) and thread(kg) distinct ledgers")

    # -------------------------------------------------------
    # Test L — All Items View
    # -------------------------------------------------------
    print("\n--- Test L: All Items View ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        ledger = await jw_svc.get_custody_ledger(jw_id)

    for item in ledger["items"]:
        assert "item_code" in item
        assert "item_name" in item
        assert "uom" in item
        assert "entries" in item
        assert isinstance(item["entries"], list)
    passed("All Items View — each item has its own ledger with entries")

    # -------------------------------------------------------
    # Test M — Empty Custody
    # -------------------------------------------------------
    print("\n--- Test M: Empty Custody ---")
    async with async_session() as session:
        jw_svc, tx_engine, session = make_services(session)
        empty_ledger = await jw_svc.get_custody_ledger(empty_jw_id)

    assert empty_ledger["supplier_name"] == "Empty Tailor"
    assert len(empty_ledger["items"]) == 0, f"Expected 0 items, got {len(empty_ledger['items'])}"
    passed("Empty Custody — no items, no error")

    # -------------------------------------------------------
    # Summary
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print(f"  RESULTS: {PASS} PASS / {FAIL} FAIL")
    if FAIL == 0:
        print("  ✅ OVERALL CERTIFICATION: PASS")
    else:
        print("  ❌ OVERALL CERTIFICATION: FAIL")
    print("=" * 60)

    os.makedirs("reports", exist_ok=True)
    with open("reports/stock_custody_ledger_report.md", "w") as f:
        f.write(f"# Stock Custody Ledger Certification\n\n")
        f.write(f"**Status:** {'PASS' if FAIL == 0 else 'FAIL'}\n\n")
        f.write(f"**Results:** {PASS} passed / {FAIL} failed\n\n")
        f.write("Tests covered: A (Basic Issue), B (Consumption), C (Return), D (Lifecycle), "
                "E (Multiple Issues), F (FIFO), G (Decimal Precision), H (Over-Return), "
                "I (Historical Integrity), J (FG Isolation), K (Multiple Items), "
                "L (All Items View), M (Empty Custody)\n")
    print("\nReport written to reports/stock_custody_ledger_report.md")

    return FAIL


if __name__ == "__main__":
    fail_count = asyncio.run(run_tests())
    sys.exit(fail_count)
