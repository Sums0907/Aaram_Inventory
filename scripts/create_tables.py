import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.foundation.database.models import BaseModel
# import all models so they get registered
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.supplier import Supplier
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.bom import BOMModel, BOMItemModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.models.balance import InventoryBalanceModel
from src.domains.inventory.models.job_work import JobWorkIssueModel, JobWorkReceiptModel, JobWorkerInventoryModel, InventoryTransformationRecord, JobWorkReturnModel, JobWorkAllocationModel
from src.domains.inventory.models.goods_receipt import GoodsReceipt, GoodsReceiptItem
from src.domains.inventory.models.sequence import SequenceModel

DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"

async def create():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    print("Tables created.")

if __name__ == "__main__":
    asyncio.run(create())
