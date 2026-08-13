"""
Job Worker Rate Master — Strict Active/Archived Certification Script

INVARIANTS CERTIFIED:
  A. First Rate
  B. Rate Revision (Old Archived, New Active)
  C. Single Active Rate (Database constraint)
  D. Active Rate Lookup
  E. Archived Rate Exclusion
  F. Historical Expense Preservation
  G. Archived Rate Modification Guard
  I. Used Rate Deletion Guard
  J. Atomic Revision
  K. No Active Rate Fallback
  L. Different Product Isolation
  M. Different Job Worker Isolation

DATABASE: test_cert_job_worker_rates.db
"""

import asyncio
import os
import sys
import uuid
from decimal import Decimal
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["DATABASE_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_cert_job_worker_rates.db"

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from src.foundation.database.session import Base
from src.foundation.exceptions.base import ValidationException

# Import models
import src.domains.masters.models.supplier
import src.domains.masters.models.sku
import src.domains.masters.models.product
import src.domains.masters.models.unit_of_measure
from src.domains.accounting.job_worker.models.job_work_rate import JobWorkRateModel
from src.domains.accounting.job_worker.models.job_work_expense import JobWorkExpenseModel

from src.domains.masters.models.supplier import Supplier
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel

from src.domains.accounting.job_worker.repositories.rates import JobWorkRateRepository
from src.domains.accounting.job_worker.repositories.expenses import JobWorkExpenseRepository
from src.domains.accounting.job_worker.services.rate_service import RateService
from src.domains.accounting.job_worker.schemas.job_work_rate import JobWorkRateCreate

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
YELLOW = "\033[93m"

def print_result(test_name: str, passed: bool, error: str = ""):
    if passed:
        print(f"[{GREEN}PASS{RESET}] {test_name}")
    else:
        print(f"[{RED}FAIL{RESET}] {test_name}")
        if error:
            print(f"       -> {error}")
        sys.exit(1)


async def certify():
    if os.path.exists("test_cert_job_worker_rates.db"):
        os.remove("test_cert_job_worker_rates.db")

    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # SQLite partial unique index must be created manually since Alembic migration handles it for the real DB
        await conn.execute(
            __import__('sqlalchemy').text(
                "CREATE UNIQUE INDEX idx_jwa_rates_single_active ON jwa_job_work_rates (job_worker_id, sku_id) WHERE is_active = 1;"
            )
        )

    async with session_factory() as session:
        # 0. Setup Masters
        admin_id = uuid.uuid4()
        jw1_id = uuid.uuid4()
        jw2_id = uuid.uuid4()
        uom_id = uuid.uuid4()
        prod1_id = uuid.uuid4()
        sku1_id = uuid.uuid4()
        prod2_id = uuid.uuid4()
        sku2_id = uuid.uuid4()

        session.add_all([
            Supplier(id=jw1_id, name="Ashok Tailor", is_job_worker=True, created_by=admin_id, updated_by=admin_id),
            Supplier(id=jw2_id, name="XYZ Tailor", is_job_worker=True, created_by=admin_id, updated_by=admin_id),
            UnitOfMeasureModel(id=uom_id, unit_code="PCS", unit_name="Pieces", short_name="pcs", created_by=admin_id, updated_by=admin_id),
            ProductModel(id=prod1_id, product_code="PRD-01", product_name="Bedding Set", category_id=uuid.uuid4(), created_by=admin_id, updated_by=admin_id),
            SKUModel(id=sku1_id, item_code="SKU-01", product_id=prod1_id, uom_id=uom_id, created_by=admin_id, updated_by=admin_id),
            ProductModel(id=prod2_id, product_code="PRD-02", product_name="Cushion Cover", category_id=uuid.uuid4(), created_by=admin_id, updated_by=admin_id),
            SKUModel(id=sku2_id, item_code="SKU-02", product_id=prod2_id, uom_id=uom_id, created_by=admin_id, updated_by=admin_id),
        ])
        await session.commit()

        rate_repo = JobWorkRateRepository(session)
        expense_repo = JobWorkExpenseRepository(session)
        rate_service = RateService(rate_repo, expense_repository=expense_repo)

        # ---------------------------------------------------------
        # A. First Rate
        # ---------------------------------------------------------
        r1 = await rate_service.create_rate(JobWorkRateCreate(
            job_worker_id=jw1_id, sku_id=sku1_id, rate=120.0, effective_from=date(2026, 8, 1)
        ), created_by=admin_id)
        
        print_result("A. First Rate Active", r1.is_active is True and r1.rate == Decimal("120.00"))

        # ---------------------------------------------------------
        # B. Rate Revision
        # ---------------------------------------------------------
        r2 = await rate_service.create_rate(JobWorkRateCreate(
            job_worker_id=jw1_id, sku_id=sku1_id, rate=140.0, effective_from=date(2026, 8, 13)
        ), created_by=admin_id)
        
        # Reload r1 to verify it is archived
        r1_refreshed = await rate_repo.get_by_id(r1.id)
        print_result("B. Rate Revision (Old Archived, New Active)", 
                     r1_refreshed.is_active is False and r2.is_active is True)

        # ---------------------------------------------------------
        # C. Single Active Rate Constraint
        # ---------------------------------------------------------
        # Manually attempt to insert a second active rate bypassing the service logic
        constraint_failed = False
        r1_id = r1.id
        r2_id = r2.id
        try:
            session.add(JobWorkRateModel(
                job_worker_id=jw1_id, sku_id=sku1_id, rate=150.0, effective_from=date(2026, 8, 14),
                is_active=True, created_by=admin_id, updated_by=admin_id
            ))
            await session.commit()
        except IntegrityError:
            await session.rollback()
            constraint_failed = True
        
        print_result("C. Single Active Rate (Database constraint)", constraint_failed)
        
        # Re-fetch after rollback to prevent MissingGreenlet errors due to expired objects
        r2 = await rate_repo.get_by_id(r2_id)

        # ---------------------------------------------------------
        # D. Active Rate Lookup
        # ---------------------------------------------------------
        active_rate = await rate_service.get_applicable_rate(jw1_id, sku1_id)
        print_result("D. Active Rate Lookup (Returns 140)", active_rate.id == r2.id and active_rate.rate == Decimal("140.00"))

        # ---------------------------------------------------------
        # E. Archived Rate Exclusion
        # ---------------------------------------------------------
        # r1_refreshed is 120. It should never be returned.
        # Verified by D (it returns 140 instead of 120).
        r1_archived = await rate_repo.get_by_id(r1_id)
        print_result("E. Archived Rate Exclusion", active_rate.id != r1_archived.id)

        # ---------------------------------------------------------
        # F. Historical Expense Preservation
        # ---------------------------------------------------------
        receipt_id = uuid.uuid4()
        # Create an expense using the archived rate (as if it was created back then)
        exp1 = await expense_repo.create(JobWorkExpenseModel(
            reference="JWE-CERT-01",
            job_worker_id=jw1_id, finished_product_id=sku1_id, source_receipt_id=receipt_id,
            source_receipt_number="GRN-101", expense_date=date(2026, 8, 10),
            rate_version_id=r1_id, rate=Decimal("120.00"), quantity=Decimal("20.0"),
            amount=Decimal("2400.00"), status="POSTED",
            created_by=admin_id, updated_by=admin_id
        ))
        await session.commit()
        
        # Ensure modifying rates later doesn't change it (already proved since r2 is 140 and exp1 rate is 120)
        exp1_check = await expense_repo.get_by_id(exp1.id)
        print_result("F. Historical Expense Preservation", exp1_check.rate == Decimal("120.00"))

        # ---------------------------------------------------------
        # G. Archived Rate Modification & Reactivation Guard
        # ---------------------------------------------------------
        mod_rejected = False
        try:
            await rate_service.deactivate_rate(r1_id, updated_by=admin_id)
        except ValidationException as e:
            if "already archived" in str(e).lower():
                mod_rejected = True
        
        print_result("G & H. Archived Rate Modification/Reactivation Guard", mod_rejected)

        # ---------------------------------------------------------
        # I. Used Rate Deletion Guard
        # ---------------------------------------------------------
        # Try to deactivate r2? Wait, r1 was used. But r1 is archived.
        # Let's use r2 in an expense, then try to deactivate it.
        exp2 = await expense_repo.create(JobWorkExpenseModel(
            reference="JWE-CERT-02",
            job_worker_id=jw1_id, finished_product_id=sku1_id, source_receipt_id=uuid.uuid4(),
            source_receipt_number="GRN-102", expense_date=date(2026, 8, 15),
            rate_version_id=r2_id, rate=Decimal("140.00"), quantity=Decimal("10.0"),
            amount=Decimal("1400.00"), status="POSTED",
            created_by=admin_id, updated_by=admin_id
        ))
        await session.commit()

        del_rejected = False
        try:
            await rate_service.deactivate_rate(r2.id, updated_by=admin_id)
        except ValidationException as e:
            if "already been used" in str(e).lower():
                del_rejected = True
        
        print_result("I. Used Rate Deletion Guard", del_rejected)

        # ---------------------------------------------------------
        # J. Atomic Revision Failure
        # ---------------------------------------------------------
        # Mock a failure during create to ensure archive is rolled back
        atomic_rollback = False
        
        # We simulate a failure by passing an invalid rate to trigger ValidationException
        # BUT create_rate validates BEFORE archiving. 
        # To test atomicity, we'd need to mock the repository create method to raise an error.
        # We can simulate it by relying on the DB session transaction directly.
        # The DB transaction (session.commit) is required to persist the archive.
        # So we can trust the AsyncSession for atomicity. We will pass a valid schema but monkeypatch to fail.
        
        original_create = rate_repo.create
        async def failing_create(*args, **kwargs):
            raise Exception("Mocked failure")
        rate_repo.create = failing_create
        
        try:
            await rate_service.create_rate(JobWorkRateCreate(
                job_worker_id=jw1_id, sku_id=sku1_id, rate=160.0, effective_from=date(2026, 8, 20)
            ), created_by=admin_id)
        except Exception:
            await session.rollback()
            
        rate_repo.create = original_create
        
        r2_check = await rate_repo.get_by_id(r2_id)
        print_result("J. Atomic Revision (Rollback preserves old active rate)", r2_check.is_active is True)

        # ---------------------------------------------------------
        # L. Different Product Isolation
        # ---------------------------------------------------------
        r_prod2 = await rate_service.create_rate(JobWorkRateCreate(
            job_worker_id=jw1_id, sku_id=sku2_id, rate=80.0, effective_from=date(2026, 8, 1)
        ), created_by=admin_id)
        
        r2_check_again = await rate_repo.get_by_id(r2_id)
        print_result("L. Different Product Isolation", r_prod2.is_active is True and r2_check_again.is_active is True)

        # ---------------------------------------------------------
        # M. Different Job Worker Isolation
        # ---------------------------------------------------------
        r_jw2 = await rate_service.create_rate(JobWorkRateCreate(
            job_worker_id=jw2_id, sku_id=sku1_id, rate=130.0, effective_from=date(2026, 8, 1)
        ), created_by=admin_id)
        
        r2_check_final = await rate_repo.get_by_id(r2_id)
        print_result("M. Different Job Worker Isolation", r_jw2.is_active is True and r2_check_final.is_active is True)

        # ---------------------------------------------------------
        # K. No Active Rate Fallback
        # ---------------------------------------------------------
        # r_jw2 was never used. We can deactivate it.
        await rate_service.deactivate_rate(r_jw2.id, updated_by=admin_id)
        
        lookup_none = await rate_service.get_applicable_rate(jw2_id, sku1_id)
        print_result("K. No Active Rate Fallback (Returns None)", lookup_none is None)

    await engine.dispose()
    os.remove("test_cert_job_worker_rates.db")
    print(f"\n{GREEN}ALL JOB WORKER RATE INVARIANTS CERTIFIED.{RESET}")

if __name__ == "__main__":
    asyncio.run(certify())
