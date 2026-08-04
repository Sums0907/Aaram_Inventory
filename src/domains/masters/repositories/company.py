from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.domains.masters.models.company import CompanyModel

class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, company_id: UUID) -> Optional[CompanyModel]:
        result = await self.session.execute(select(CompanyModel).filter(CompanyModel.id == company_id))
        return result.scalars().first()
        
    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(CompanyModel))
        return result.scalar() or 0

    async def get_by_code(self, company_code: str) -> Optional[CompanyModel]:
        result = await self.session.execute(select(CompanyModel).filter(CompanyModel.company_code == company_code))
        return result.scalars().first()
        
    async def get_by_name(self, company_name: str) -> Optional[CompanyModel]:
        result = await self.session.execute(select(CompanyModel).filter(CompanyModel.company_name == company_name))
        return result.scalars().first()
        
    async def get_by_gstin(self, gstin: str) -> Optional[CompanyModel]:
        result = await self.session.execute(select(CompanyModel).filter(CompanyModel.gstin == gstin))
        return result.scalars().first()
        
    async def get_by_pan(self, pan: str) -> Optional[CompanyModel]:
        result = await self.session.execute(select(CompanyModel).filter(CompanyModel.pan == pan))
        return result.scalars().first()

    async def create(self, company: CompanyModel) -> CompanyModel:
        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return company

    async def update(self, company: CompanyModel) -> CompanyModel:
        await self.session.commit()
        await self.session.refresh(company)
        return company
