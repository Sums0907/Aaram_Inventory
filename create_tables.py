import asyncio
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.foundation.database.models import BaseModel
from src.app.container import DomainsContainer
from src.foundation.configuration import get_settings
from src.domains.inventory.models.job_work import JobWorkIssueModel, JobWorkReturnModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.data_ingestion.models.packer_event import PackerEventModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel

async def create():
    settings = get_settings()
    domains_container = DomainsContainer()
    domains_container.core.config.from_dict(settings.model_dump())
    
    engine = domains_container.core.db()._engine
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
        print("Created tables")

if __name__ == "__main__":
    asyncio.run(create())
