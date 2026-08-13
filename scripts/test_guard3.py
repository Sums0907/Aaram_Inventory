import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.foundation.database.session import Base
from sqlalchemy import delete
from src.domains.masters.models.supplier import Supplier
import uuid

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"

async def test_guard():
    print("Testing Guard against session.delete()...")
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with TestingSessionLocal() as session:
        # Create a dummy supplier
        sup = Supplier(id=uuid.uuid4(), name="Dummy")
        session.add(sup)
        await session.commit()
        
        # Now try to delete it with CRUD
        await session.delete(sup)
        await session.commit()
        print("CRUD delete successful!")

if __name__ == "__main__":
    asyncio.run(test_guard())
