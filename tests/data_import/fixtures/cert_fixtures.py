"""
Shared fixtures for the Master Data Import Certification Suite.
All tests use isolated in-memory SQLite databases — no dev/staging/prod DB is touched.
"""
import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.foundation.database.models import BaseModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.supplier import Supplier
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.pricing import PricingModel
from src.domains.masters.models.packaging import PackagingModel
from src.domains.masters.models.bom import BOMModel, BOMItemModel
from src.foundation.enums.status import GenericStatus

# Import all models to populate metadata
import src.domains.masters.models.company
import src.domains.masters.models.warehouse
import src.domains.masters.models.product_attribute
import src.domains.operations.models.sales_order
import src.domains.operations.models.tax_invoice
import src.domains.operations.models.payment
import src.domains.operations.models.settlement
import src.domains.operations.models.refund
import src.domains.data_ingestion.models.integration
import src.domains.data_ingestion.models.import_job
import src.domains.data_ingestion.models.import_file
import src.domains.data_ingestion.models.import_record
import src.domains.data_ingestion.models.import_error
import src.domains.data_ingestion.models.import_summary
import src.domains.data_ingestion.models.import_audit_log

CERT_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def cert_session():
    """Fully isolated in-memory DB for each certification test. Guaranteed clean state."""
    engine = create_async_engine(CERT_DB_URL, echo=False)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    await engine.dispose()


async def seed_uom(session, unit_code="MTR", unit_name="Meter", unit_type="DECIMAL", short_name=None):
    uom = UnitOfMeasureModel(
        id=uuid.uuid4(), unit_code=unit_code, unit_name=unit_name,
        unit_type=unit_type, short_name=short_name or unit_code.lower()
    )
    session.add(uom)
    await session.flush()
    return uom


async def seed_category(session, code, name, parent_id=None):
    cat = CategoryModel(id=uuid.uuid4(), category_code=code, category_name=name,
                        parent_id=parent_id, status=GenericStatus.ACTIVE)
    session.add(cat)
    await session.flush()
    return cat


async def seed_supplier(session, name, phone=None, gstin=None, is_job_worker=False):
    sup = Supplier(id=uuid.uuid4(), name=name, contact_number=phone,
                   gstin=gstin, is_job_worker=is_job_worker)
    session.add(sup)
    await session.flush()
    return sup


async def seed_sku(session, item_code, product_code=None, sku_code=None, barcode=None, uom_id=None):
    prod = ProductModel(id=uuid.uuid4(), product_code=product_code or item_code,
                        product_name=item_code)
    session.add(prod)
    await session.flush()
    sku = SKUModel(id=uuid.uuid4(), item_code=item_code,
                   sku_code=sku_code, product_id=prod.id,
                   barcode=barcode, uom_id=uom_id, attribute_values={})
    pricing = PricingModel(id=uuid.uuid4(), sku_id=sku.id,
                           selling_price=100, mrp=150, cost_price=80, gst_percentage=12)
    packaging = PackagingModel(id=uuid.uuid4(), sku_id=sku.id)
    session.add(sku)
    session.add(pricing)
    session.add(packaging)
    await session.flush()
    return sku
