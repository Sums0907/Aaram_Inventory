from typing import List
from uuid import UUID
from src.domains.data_ingestion.repositories.integration import IntegrationRepository
from src.domains.data_ingestion.models.integration import IntegrationModel
from src.domains.data_ingestion.schemas.integration import IntegrationCreate, IntegrationUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException
from src.foundation.enums.status import GenericStatus

class IntegrationService:
    def __init__(self, repository: IntegrationRepository):
        self.repository = repository

    async def get_integration(self, integration_id: UUID) -> IntegrationModel:
        integration = await self.repository.get_by_id(integration_id)
        if not integration:
            raise NotFoundException(message="Integration not found")
        return integration

    async def list_integrations(self, skip: int = 0, limit: int = 100) -> List[IntegrationModel]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create_integration(self, schema: IntegrationCreate, created_by: UUID) -> IntegrationModel:
        existing = await self.repository.get_by_code(schema.integration_code)
        if existing:
            raise ValidationException(message="Integration Code must be unique")

        integration = IntegrationModel(
            **schema.model_dump(),
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(integration)

    async def update_integration(self, integration_id: UUID, schema: IntegrationUpdate, updated_by: UUID) -> IntegrationModel:
        integration = await self.get_integration(integration_id)
        
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(integration, key, value)
            
        integration.updated_by = updated_by
        return await self.repository.update(integration)

    async def activate_integration(self, integration_id: UUID, updated_by: UUID) -> IntegrationModel:
        integration = await self.get_integration(integration_id)
        if integration.status == GenericStatus.ACTIVE:
            raise ValidationException(message="Integration is already active")
        integration.status = GenericStatus.ACTIVE
        integration.updated_by = updated_by
        return await self.repository.update(integration)

    async def deactivate_integration(self, integration_id: UUID, updated_by: UUID) -> IntegrationModel:
        integration = await self.get_integration(integration_id)
        if integration.status == GenericStatus.INACTIVE:
            raise ValidationException(message="Integration is already inactive")
        integration.status = GenericStatus.INACTIVE
        integration.updated_by = updated_by
        return await self.repository.update(integration)

    async def archive_integration(self, integration_id: UUID, updated_by: UUID) -> IntegrationModel:
        integration = await self.get_integration(integration_id)
        if integration.status == GenericStatus.ARCHIVED:
            raise ValidationException(message="Integration is already archived")
        integration.status = GenericStatus.ARCHIVED
        integration.updated_by = updated_by
        return await self.repository.update(integration)
