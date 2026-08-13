import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.foundation.database.session import Base
from sqlalchemy import delete
from src.domains.masters.models.supplier import Supplier

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"

async def test_guard():
    print("Testing Guard against drop_all...")
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception as e:
        print(f"Caught exception: {e}")
        
    print("\nTesting Guard against session.execute(delete(Supplier))...")
    try:
        async with TestingSessionLocal() as session:
            await session.execute(delete(Supplier))
            await session.commit()
    except Exception as e:
        print(f"Caught exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_guard())
