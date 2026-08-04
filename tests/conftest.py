import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.foundation.configuration import get_settings
from src.foundation.database.models import BaseModel
from src.app.main import app

settings = get_settings()
# Use a separate test database URL if possible, otherwise this is a placeholder
TEST_DATABASE_URL = settings.DATABASE_URL + "_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
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
    from uuid import uuid7
    
    # Mock Auth
    mock_user = CurrentUser(id=str(uuid7()), username="test_admin", role="admin")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
        
    app.dependency_overrides.clear()
