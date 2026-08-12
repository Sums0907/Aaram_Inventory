"""
Job Worker Accounting — Certification Script

INVARIANTS CERTIFIED:
  1. Rate creation and effective-date lookup
  2. Rate versioning (historical rates preserved)
  3. Missing rate detection (returns None, no ₹0 expense)
  4. Expense creation from JW Receipt with rate snapshot
  5. Correct Decimal arithmetic (quantity × rate)
  6. Duplicate receipt guard
  7. Payment recording and FIFO allocation
  8. Partial payment: outstanding reduces correctly
  9. Multiple payments: outstanding reduces correctly
  10. Full chain: Receipt → Expense → Payable → Payment → Outstanding

DATABASE: test_cert_job_worker_accounting.db (NEVER touches test_manual.db)
"""

import asyncio
import os
import sys
import uuid
from decimal import Decimal
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["DATABASE_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_cert_job_worker_accounting.db"

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.foundation.database.session import Base

# Import all models so Base.metadata is aware of new tables
import src.domains.masters.models.supplier
import src.domains.masters.models.sku
import src.domains.masters.models.product
import src.domains.masters.models.unit_of_measure
import src.domains.masters.models.warehouse
import src.domains.masters.models.bom
import src.domains.inventory.models.movement
import src.domains.inventory.models.balance
import src.domains.inventory.models.job_work
import src.domains.inventory.models.goods_receipt
import src.domains.accounting.models.journal
import src.domains.accounting.models.ledger
from src.domains.accounting.job_worker.models.job_work_rate import JobWorkRateModel
from src.domains.accounting.job_worker.models.job_work_expense import JobWorkExpenseModel
from src.domains.accounting.job_worker.models.job_worker_payment import JobWorkerPaymentModel
from src.domains.accounting.job_worker.models.payable_allocation import PayableAllocationModel

from src.domains.masters.models.supplier import Supplier
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel

from src.domains.accounting.job_worker.repositories.rates import JobWorkRateRepository
from src.domains.accounting.job_worker.repositories.expenses import JobWorkExpenseRepository
from src.domains.accounting.job_worker.repositories.payments import JobWorkerPaymentRepository
from src.domains.accounting.job_worker.repositories.payable import PayableRepository
from src.domains.accounting.job_worker.services.rate_service import RateService
from src.domains.accounting.job_worker.services.expense_service import ExpenseService
from src.domains.accounting.job_worker.services.payment_service import PaymentService
from src.domains.accounting.job_worker.services.payable_service import PayableService
from src.domains.accounting.job_worker.schemas.job_work_rate import JobWorkRateCreate
from src.domains.accounting.job_worker.schemas.job_worker_payment import JobWorkerPaymentCreate

# Safety guard
assert os.environ.get("DATABASE_ENV") == "test", "FATAL: DATABASE_ENV must be 'test'"
assert "test_cert_job_worker_accounting" in os.environ["DATABASE_URL"], "FATAL: must use cert DB"

DB_URL = os.environ["DATABASE_URL"]
engine = create_async_engine(DB_URL)
SessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

SYS_USER = uuid.UUID("00000000-0000-0000-0000-000000000001")

PASS = 0
FAIL = 0

def ok(name: str):
    global PASS
    PASS += 1
    print(f"  ✅ PASS  {name}")

def fail(name: str, err):
    global FAIL
    FAIL += 1
    print(f"  ❌ FAIL  {name}: {err}")


async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_fixtures(session: AsyncSession):
    uom = UnitOfMeasureModel(unit_code="PCS-C", unit_name="Pieces-C", short_name="pcs", unit_type="INTEGER")
    session.add(uom)
    await session.flush()

    jw = Supplier(name="Test Tailor", is_job_worker=True)
    jw2 = Supplier(name="Another Tailor", is_job_worker=True)
    session.add_all([jw, jw2])

    p = ProductModel(product_code="FG-001", product_name="Bedding Set", item_type="FINISHED_GOOD")
    p2 = ProductModel(product_code="FG-002", product_name="Bedsheet", item_type="FINISHED_GOOD")
    session.add_all([p, p2])
    await session.flush()

    sku = SKUModel(product_id=p.id, sku_code="SKU-FG-001", item_code="ITM-FG-001", uom_id=uom.id)
    sku2 = SKUModel(product_id=p2.id, sku_code="SKU-FG-002", item_code="ITM-FG-002", uom_id=uom.id)
    session.add_all([sku, sku2])
    await session.flush()

    return jw, jw2, sku, sku2


async def run_certifications():
    await setup_db()

    async with SessionFactory() as session:
        jw, jw2, sku, sku2 = await create_fixtures(session)
        await session.flush()

        rate_repo = JobWorkRateRepository(session)
        expense_repo = JobWorkExpenseRepository(session)
        payment_repo = JobWorkerPaymentRepository(session)
        payable_repo = PayableRepository(session)

        rate_svc = RateService(rate_repo)
        expense_svc = ExpenseService(expense_repo, rate_repo)
        payment_svc = PaymentService(payment_repo, expense_repo, payable_repo)
        payable_svc = PayableService(expense_repo, payment_repo, payable_repo)

        today = date.today()
        aug1 = date(2026, 8, 1)
        aug15 = date(2026, 8, 15)
        sep1 = date(2026, 9, 1)

        # -------------------------------------------------------------------
        # 1. Create rate
        # -------------------------------------------------------------------
        try:
            r1 = await rate_svc.create_rate(
                JobWorkRateCreate(job_worker_id=jw.id, sku_id=sku.id, rate=80.0, effective_from=aug1),
                created_by=SYS_USER
            )
            await session.flush()
            assert r1.rate == Decimal("80.00")
            ok("Create Job Work Rate")
        except Exception as e:
            fail("Create Job Work Rate", e)

        # -------------------------------------------------------------------
        # 2. Retrieve applicable rate on aug15
        # -------------------------------------------------------------------
        try:
            found = await rate_svc.get_applicable_rate(jw.id, sku.id, aug15)
            assert found is not None
            assert Decimal(str(found.rate)) == Decimal("80.00")
            ok("Retrieve applicable rate (aug15)")
        except Exception as e:
            fail("Retrieve applicable rate (aug15)", e)

        # -------------------------------------------------------------------
        # 3. Rate versioning — create sep rate
        # -------------------------------------------------------------------
        try:
            r2 = await rate_svc.create_rate(
                JobWorkRateCreate(job_worker_id=jw.id, sku_id=sku.id, rate=85.0, effective_from=sep1),
                created_by=SYS_USER
            )
            await session.flush()
            # Aug still returns ₹80
            aug_rate = await rate_svc.get_applicable_rate(jw.id, sku.id, aug15)
            sep_rate = await rate_svc.get_applicable_rate(jw.id, sku.id, sep1)
            assert Decimal(str(aug_rate.rate)) == Decimal("80.00"), f"Expected 80, got {aug_rate.rate}"
            assert Decimal(str(sep_rate.rate)) == Decimal("85.00"), f"Expected 85, got {sep_rate.rate}"
            ok("Rate versioning (aug=₹80, sep=₹85)")
        except Exception as e:
            fail("Rate versioning", e)

        # -------------------------------------------------------------------
        # 4. Missing rate returns None
        # -------------------------------------------------------------------
        try:
            missing = await rate_svc.get_applicable_rate(jw2.id, sku.id, aug15)
            assert missing is None
            ok("Missing rate returns None (not ₹0)")
        except Exception as e:
            fail("Missing rate returns None", e)

        # -------------------------------------------------------------------
        # 5. Different workers / products have independent rates
        # -------------------------------------------------------------------
        try:
            await rate_svc.create_rate(
                JobWorkRateCreate(job_worker_id=jw2.id, sku_id=sku.id, rate=75.0, effective_from=aug1),
                created_by=SYS_USER
            )
            await rate_svc.create_rate(
                JobWorkRateCreate(job_worker_id=jw.id, sku_id=sku2.id, rate=45.0, effective_from=aug1),
                created_by=SYS_USER
            )
            await session.flush()
            r_jw2 = await rate_svc.get_applicable_rate(jw2.id, sku.id, aug15)
            r_sku2 = await rate_svc.get_applicable_rate(jw.id, sku2.id, aug15)
            assert Decimal(str(r_jw2.rate)) == Decimal("75.00")
            assert Decimal(str(r_sku2.rate)) == Decimal("45.00")
            ok("Independent rates per worker and per product")
        except Exception as e:
            fail("Independent rates per worker/product", e)

        # -------------------------------------------------------------------
        # 6. Expense creation from receipt: 100 pcs × ₹80 = ₹8,000
        # -------------------------------------------------------------------
        fake_receipt_id = uuid.uuid4()
        try:
            exp = await expense_svc.create_from_receipt(
                job_worker_id=jw.id,
                sku_id=sku.id,
                quantity=100.0,
                receipt_id=fake_receipt_id,
                receipt_number="GRN-001",
                receipt_date=aug15,
                created_by=SYS_USER,
            )
            await session.flush()
            assert exp is not None
            assert Decimal(str(exp.amount)) == Decimal("8000.00"), f"Expected 8000, got {exp.amount}"
            assert Decimal(str(exp.rate)) == Decimal("80.00")
            assert str(exp.source_receipt_number) == "GRN-001"
            ok("Expense from receipt: 100 × ₹80 = ₹8,000")
        except Exception as e:
            fail("Expense creation from receipt", e)

        # -------------------------------------------------------------------
        # 7. Rate snapshot — expense amount unchanged even if rate changes
        # -------------------------------------------------------------------
        try:
            # The August expense must remain ₹8,000 regardless of sep rate
            expenses = await expense_repo.get_all_for_worker(jw.id)
            aug_expense = next((e for e in expenses if str(e.source_receipt_number) == "GRN-001"), None)
            assert aug_expense is not None
            assert Decimal(str(aug_expense.amount)) == Decimal("8000.00")
            assert Decimal(str(aug_expense.rate)) == Decimal("80.00")  # snapshot preserved
            ok("Rate snapshot immutability")
        except Exception as e:
            fail("Rate snapshot immutability", e)

        # -------------------------------------------------------------------
        # 8. Duplicate receipt guard
        # -------------------------------------------------------------------
        try:
            from src.foundation.exceptions.base import ValidationException
            raised = False
            try:
                await expense_svc.create_from_receipt(
                    job_worker_id=jw.id, sku_id=sku.id, quantity=100.0,
                    receipt_id=fake_receipt_id, receipt_number="GRN-001",
                    receipt_date=aug15, created_by=SYS_USER,
                )
            except ValidationException:
                raised = True
            assert raised, "Expected ValidationException for duplicate receipt"
            ok("Duplicate receipt guard")
        except Exception as e:
            fail("Duplicate receipt guard", e)

        # -------------------------------------------------------------------
        # 9. Create another expense (GRN-004: 50 pcs × ₹80 = ₹4,000)
        # -------------------------------------------------------------------
        try:
            exp2 = await expense_svc.create_from_receipt(
                job_worker_id=jw.id,
                sku_id=sku.id,
                quantity=50.0,
                receipt_id=uuid.uuid4(),
                receipt_number="GRN-004",
                receipt_date=aug15,
                created_by=SYS_USER,
            )
            await session.flush()
            assert Decimal(str(exp2.amount)) == Decimal("4000.00")
            ok("Second expense: 50 × ₹80 = ₹4,000")
        except Exception as e:
            fail("Second expense", e)

        # -------------------------------------------------------------------
        # 10. Payable totals: total_exp=12000, total_paid=0, outstanding=12000
        # -------------------------------------------------------------------
        try:
            total_exp, total_paid = await payable_repo.get_totals_for_worker(jw.id)
            assert total_exp == Decimal("12000.00"), f"Expected 12000, got {total_exp}"
            assert total_paid == Decimal("0.00")
            ok("Payable totals: ₹12,000 outstanding before payment")
        except Exception as e:
            fail("Payable totals before payment", e)

        # -------------------------------------------------------------------
        # 11. Partial payment: ₹7,000
        # -------------------------------------------------------------------
        try:
            pay1 = await payment_svc.record_payment(
                JobWorkerPaymentCreate(
                    job_worker_id=jw.id,
                    payment_date=aug15,
                    amount=7000.0,
                    payment_account="Axis Bank",
                    payment_reference="UTR123",
                ),
                created_by=SYS_USER,
            )
            await session.flush()
            total_exp, total_paid = await payable_repo.get_totals_for_worker(jw.id)
            outstanding = total_exp - total_paid
            assert outstanding == Decimal("5000.00"), f"Expected 5000, got {outstanding}"
            ok("Partial payment ₹7,000 → Outstanding ₹5,000")
        except Exception as e:
            fail("Partial payment", e)

        # -------------------------------------------------------------------
        # 12. Second payment: ₹3,000 → Outstanding ₹2,000
        # -------------------------------------------------------------------
        try:
            await payment_svc.record_payment(
                JobWorkerPaymentCreate(
                    job_worker_id=jw.id,
                    payment_date=aug15,
                    amount=3000.0,
                    payment_account="Cash",
                ),
                created_by=SYS_USER,
            )
            await session.flush()
            total_exp, total_paid = await payable_repo.get_totals_for_worker(jw.id)
            outstanding = total_exp - total_paid
            assert outstanding == Decimal("2000.00"), f"Expected 2000, got {outstanding}"
            ok("Second payment ₹3,000 → Outstanding ₹2,000")
        except Exception as e:
            fail("Second payment", e)

        # -------------------------------------------------------------------
        # 13. Overpayment rejected
        # -------------------------------------------------------------------
        try:
            from src.foundation.exceptions.base import ValidationException
            raised = False
            try:
                await payment_svc.record_payment(
                    JobWorkerPaymentCreate(
                        job_worker_id=jw.id, payment_date=aug15, amount=99999.0
                    ),
                    created_by=SYS_USER,
                )
            except ValidationException:
                raised = True
            assert raised
            ok("Overpayment rejected")
        except Exception as e:
            fail("Overpayment rejected", e)

        # -------------------------------------------------------------------
        # 14. Payable ledger builds correctly (chronological, running balance)
        # -------------------------------------------------------------------
        try:
            ledger = await payable_svc.get_payable_ledger(jw.id, "Test Tailor")
            assert ledger.outstanding == 2000.0, f"Expected 2000, got {ledger.outstanding}"
            assert len(ledger.entries) >= 4  # 2 expenses + 2 payments
            ok("Payable ledger builds correctly")
        except Exception as e:
            fail("Payable ledger", e)

        # -------------------------------------------------------------------
        # 15. No expense created if no rate configured for worker
        # -------------------------------------------------------------------
        try:
            # jw2 has no rate for sku2
            result = await expense_svc.create_from_receipt(
                job_worker_id=jw2.id,
                sku_id=sku2.id,
                quantity=50.0,
                receipt_id=uuid.uuid4(),
                receipt_number="GRN-X01",
                receipt_date=aug15,
                created_by=SYS_USER,
            )
            assert result is None, "Expected None when no rate configured"
            ok("No expense created when rate not configured")
        except Exception as e:
            fail("No expense when rate missing", e)

        # -------------------------------------------------------------------
        # 16. Rate override works: 50 pcs × ₹90 = ₹4,500
        # -------------------------------------------------------------------
        try:
            overridden = await expense_svc.create_from_receipt(
                job_worker_id=jw2.id,
                sku_id=sku2.id,
                quantity=50.0,
                receipt_id=uuid.uuid4(),
                receipt_number="GRN-X02",
                receipt_date=aug15,
                created_by=SYS_USER,
                rate_override=90.0,
            )
            await session.flush()
            assert overridden is not None
            assert Decimal(str(overridden.amount)) == Decimal("4500.00")
            ok("Rate override: 50 × ₹90 = ₹4,500")
        except Exception as e:
            fail("Rate override", e)

        await session.commit()

    # Clean up test DB
    import os as _os
    try:
        _os.remove("test_cert_job_worker_accounting.db")
    except Exception:
        pass

    # -------------------------------------------------------------------
    # Report
    # -------------------------------------------------------------------
    print()
    print("=" * 55)
    print("  Job Worker Accounting — Certification Report")
    print("=" * 55)
    print(f"  PASS: {PASS}   FAIL: {FAIL}")
    if FAIL == 0:
        print("  STATUS: ✅ CERTIFIED")
    else:
        print("  STATUS: ❌ FAILED — do not promote to production")
    print("=" * 55)
    return FAIL


if __name__ == "__main__":
    result = asyncio.run(run_certifications())
    sys.exit(0 if result == 0 else 1)
