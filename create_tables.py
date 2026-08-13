import asyncio
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.db import get_engine
from src.foundation.database.models import BaseModel
from src.domains.inventory.models.job_work import JobWorkIssueModel, JobWorkReturnModel

async def create():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
        print("Created tables")

asyncio.run(create())
