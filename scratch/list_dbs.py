import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def list_dbs():
    engine = create_async_engine("postgresql+asyncpg://postgres:password@localhost:5433/postgres")
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        dbs = [row[0] for row in result]
        print("Databases:", dbs)

asyncio.run(list_dbs())
