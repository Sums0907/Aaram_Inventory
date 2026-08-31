import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres:password@localhost:5433/inventory_dev")
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT pid, wait_event_type, wait_event, query FROM pg_stat_activity WHERE state = 'active' OR wait_event IS NOT NULL"))
        for row in result:
            print(row)

asyncio.run(main())
