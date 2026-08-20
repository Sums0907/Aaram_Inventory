import os
os.environ["DATABASE_ENV"] = "test"
import pytest_asyncio
import pytest
from dependency_injector import providers
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.foundation.configuration import get_settings
from src.foundation.database.models import BaseModel
from src.app.main import app

settings = get_settings()
# Use aiosqlite for tests because docker/postgres is not installed
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

from src.foundation.database.session import Database
app.core_container.db.override(
    providers.Singleton(Database, db_url=TEST_DATABASE_URL, debug=False, pool_size=1, max_overflow=0)
)

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    # Ensure all models are imported before creating metadata
    import src.domains.masters.models.company
    import src.domains.masters.models.unit_of_measure
    import src.domains.masters.models.warehouse
    import src.domains.masters.models.category
    import src.domains.masters.models.product_attribute
    import src.domains.masters.models.sku
    
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

    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    await test_engine.dispose()

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    from src.foundation.authentication.dependencies import get_current_user, CurrentUser
    from uuid_extensions import uuid7
    
    # Mock Auth
    mock_user = CurrentUser(
        user_id=str(uuid7()),
        name="test_admin",
        applications=["AARAM_BOOKS"],
        roles=["OWNER"],
        permissions=["PRODUCT_VIEW", "PRODUCT_CREATE", "PRODUCT_UPDATE", "INVENTORY_RECEIPT_VIEW", "INVENTORY_RECEIPT_CREATE", "INVENTORY_RETURN_VIEW", "INVENTORY_RETURN_CREATE", "INVENTORY_ADJUSTMENT_CREATE", "INVENTORY_VERIFICATION_EXECUTE", "INVENTORY_EXCEPTION_VIEW", "INVENTORY_EXCEPTION_RESOLVE", "INVENTORY_TRANSFORMATION_CREATE", "INVENTORY_JOBWORK_VIEW", "INVENTORY_JOBWORK_MANAGE", "INVENTORY_ACTIVITY_VIEW", "CATALOG_VIEW", "MASTER_DATA_IMPORT"]
    )
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
        
    app.dependency_overrides.clear()
