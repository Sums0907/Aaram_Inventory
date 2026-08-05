from uuid import UUID
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.accounting.models.journal import JournalEntryModel, JournalLineModel
from src.domains.accounting.schemas.journal import JournalEntryCreate

class JournalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_journal(self, data: JournalEntryCreate, created_by: UUID) -> JournalEntryModel:
        journal_dict = data.model_dump(exclude={"lines"})
        journal_dict["created_by"] = created_by
        journal_dict["updated_by"] = created_by
        
        db_journal = JournalEntryModel(**journal_dict)
        
        for line_data in data.lines:
            line_dict = line_data.model_dump()
            line_dict["created_by"] = created_by
            line_dict["updated_by"] = created_by
            db_line = JournalLineModel(**line_dict)
            db_journal.lines.append(db_line)
            
        self.session.add(db_journal)
        await self.session.commit()
        await self.session.refresh(db_journal)
        return db_journal
        
    async def get_by_journal_number(self, journal_number: str) -> Optional[JournalEntryModel]:
        stmt = select(JournalEntryModel).where(JournalEntryModel.journal_number == journal_number)
        result = await self.session.execute(stmt)
        return result.scalars().first()
