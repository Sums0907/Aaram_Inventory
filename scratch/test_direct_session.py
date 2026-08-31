import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

async def main():
    db_url = "postgresql+asyncpg://postgres:password@localhost:5433/inventory_dev"
    engine = create_async_engine(db_url, echo=True, pool_size=5)
    factory = async_sessionmaker(engine, class_=AsyncSession)
    
    print("Getting session...")
    async with factory() as session:
        print("Executing query...")
        result = await session.execute(text("SELECT 1"))
        print(f"Result: {result.scalar()}")

asyncio.run(main())
