from uuid import UUID
from src.domains.masters.repositories.company import CompanyRepository
from src.domains.masters.models.company import CompanyModel
from src.domains.masters.schemas.company import CompanyCreate, CompanyUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException, AlreadyExistsException
from src.foundation.enums.status import GenericStatus

class CompanyService:
    def __init__(self, repository: CompanyRepository):
        self.repository = repository

    async def get_company(self, company_id: UUID) -> CompanyModel:
        company = await self.repository.get_by_id(company_id)
        if not company:
            raise NotFoundException(message="Company not found")
        return company
        
    async def create_company(self, schema: CompanyCreate, created_by: UUID) -> CompanyModel:
        # Enforce single-company rule for Version 1
        if await self.repository.count() > 0:
            raise AlreadyExistsException(message="Company already initialized.")
            
        # Business Validation: Uniqueness
        if await self.repository.get_by_code(schema.company_code):
            raise ValidationException(message="Company Code must be unique")
        if await self.repository.get_by_name(schema.company_name):
            raise ValidationException(message="Company Name must be unique")
        if await self.repository.get_by_gstin(schema.gstin):
            raise ValidationException(message="GSTIN must be unique")
        if await self.repository.get_by_pan(schema.pan):
            raise ValidationException(message="PAN must be unique")
            
        company = CompanyModel(
            **schema.model_dump(),
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(company)

    async def update_company(self, company_id: UUID, schema: CompanyUpdate, updated_by: UUID) -> CompanyModel:
        company = await self.get_company(company_id)
        
        # Business Validation: Uniqueness (Exclude self)
        existing_name = await self.repository.get_by_name(schema.company_name)
        if existing_name and existing_name.id != company.id:
            raise ValidationException(message="Company Name must be unique")
            
        existing_gstin = await self.repository.get_by_gstin(schema.gstin)
        if existing_gstin and existing_gstin.id != company.id:
            raise ValidationException(message="GSTIN must be unique")
            
        existing_pan = await self.repository.get_by_pan(schema.pan)
        if existing_pan and existing_pan.id != company.id:
            raise ValidationException(message="PAN must be unique")

        # Apply updates
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(company, key, value)
            
        company.updated_by = updated_by
        return await self.repository.update(company)
        
    async def activate_company(self, company_id: UUID, updated_by: UUID) -> CompanyModel:
        company = await self.get_company(company_id)
        if company.status == GenericStatus.ACTIVE:
            raise ValidationException(message="Company is already active")
        company.status = GenericStatus.ACTIVE
        company.updated_by = updated_by
        return await self.repository.update(company)

    async def deactivate_company(self, company_id: UUID, updated_by: UUID) -> CompanyModel:
        company = await self.get_company(company_id)
        if company.status == GenericStatus.INACTIVE:
            raise ValidationException(message="Company is already inactive")
        company.status = GenericStatus.INACTIVE
        company.updated_by = updated_by
        return await self.repository.update(company)
