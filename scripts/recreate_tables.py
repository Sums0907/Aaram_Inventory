import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.foundation.database.models import BaseModel
from src.domains.masters.models import *
from src.domains.inventory.models import *
from src.domains.accounting.models import *
from src.domains.connectors.models import *

async def create_tables():
    engine = create_async_engine("sqlite+aiosqlite:///./test_manual.db", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())
