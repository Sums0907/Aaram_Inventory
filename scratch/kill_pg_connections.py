import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres:password@localhost:5433/inventory_dev")
    async with engine.connect() as conn:
        await conn.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = 'inventory_dev'"))
        print("Killed all other connections.")

asyncio.run(main())
