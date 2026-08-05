import pytest
from uuid_extensions import uuid7
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.data_ingestion.repositories.integration import IntegrationRepository
from src.domains.data_ingestion.services.integration import IntegrationService
from src.domains.data_ingestion.schemas.integration import IntegrationCreate
from src.foundation.exceptions.base import ValidationException

@pytest.mark.asyncio
async def test_service_create_success(db_session: AsyncSession):
    repo = IntegrationRepository(db_session)
    service = IntegrationService(repo)
    user_id = uuid7()
    
    schema = IntegrationCreate(
        integration_code="AMZ",
        integration_name="Amazon",
        integration_type="MARKETPLACE"
    )
    
    integration = await service.create_integration(schema, created_by=user_id)
    assert integration.integration_code == "AMZ"

@pytest.mark.asyncio
async def test_service_create_duplicate(db_session: AsyncSession):
    repo = IntegrationRepository(db_session)
    service = IntegrationService(repo)
    user_id = uuid7()
    
    schema = IntegrationCreate(
        integration_code="FLIPKART",
        integration_name="Flipkart",
        integration_type="MARKETPLACE"
    )
    
    await service.create_integration(schema, created_by=user_id)
    
    with pytest.raises(ValidationException) as exc:
        await service.create_integration(schema, created_by=user_id)
        
    assert "Integration Code must be unique" in str(exc.value)
