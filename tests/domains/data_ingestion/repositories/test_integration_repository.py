import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.data_ingestion.models.integration import IntegrationModel
from src.domains.data_ingestion.repositories.integration import IntegrationRepository

@pytest.mark.asyncio
async def test_repository_create_and_get(db_session: AsyncSession):
    repo = IntegrationRepository(db_session)
    
    integration = IntegrationModel(
        integration_code="VYAPAR",
        integration_name="Vyapar Accounting",
        integration_type="ACCOUNTING"
    )
    
    created = await repo.create(integration)
    assert created.id is not None
    assert created.integration_code == "VYAPAR"
    
    fetched = await repo.get_by_code("VYAPAR")
    assert fetched is not None
    assert fetched.id == created.id
