import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.foundation.database.session import Base
from src.domains.accounting.models.ledger import LedgerModel
import sys
import os

def require_test_environment():
    env = os.environ.get("DATABASE_ENV", "development").lower()
    if env != "test":
        print("DATABASE RESET REQUEST\n")
        print("Environment:\n" + env.upper())
        print("\nDestructive operation:\nBLOCKED")
        print("\nDATABASE_ENV must be 'test' to run reset_db.py")
        sys.exit(1)
        
    db_url = os.environ.get("RESET_DATABASE_URL")
    if not db_url:
        print("DATABASE RESET REQUEST\n")
        print("RESET_DATABASE_URL environment variable is required.")
        print("Example: RESET_DATABASE_URL=sqlite+aiosqlite:///test_cert_reset.db")
        sys.exit(1)
        
    if "test_manual" in db_url or "prod" in db_url:
        print("DATABASE RESET REQUEST\n")
        print(f"Target:\n{db_url}")
        print("\nDestructive operation:\nBLOCKED")
        print("\nCannot reset a development or production database.")
        sys.exit(1)
        
    print("DATABASE RESET REQUEST\n")
    print(f"Target:\n{db_url}")
    print("\nEnvironment:\nTEST")
    print("\nDestructive operation:\nALLOWED\n\nProceeding...")
    return db_url

TEST_DATABASE_URL = require_test_environment()

# Import all models to register them with Base.metadata
from src.domains.masters.models import CategoryModel, UnitOfMeasureModel, ProductAttributeModel, ProductModel, SKUModel, CompanyModel, WarehouseModel, PricingModel, PackagingModel, ProductImageModel
from src.domains.data_ingestion.models.integration import IntegrationModel
from src.domains.data_ingestion.models.import_job import ImportJobModel
from src.domains.data_ingestion.models.import_file import ImportFileModel
from src.domains.data_ingestion.models.import_record import ImportRecordModel
from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.models.tax_invoice import TaxInvoiceModel
from src.domains.operations.models.payment import PaymentModel
from src.domains.operations.models.settlement import SettlementModel
from src.domains.matching.models.job import MatchJobModel
from src.domains.matching.models.relationship import MatchRelationshipModel
from src.domains.matching.models.exception import MatchExceptionModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.models.balance import InventoryBalanceModel
from src.domains.inventory.models.exception import InventoryExceptionModel
from src.domains.inventory.models.goods_receipt import GoodsReceipt, GoodsReceiptItem
from src.domains.inventory.models.job_work import JobWorkIssueModel, JobWorkReturnModel, JobWorkReceiptModel, JobWorkerInventoryModel

from src.domains.masters.models.bom import BOMModel, BOMItemModel
from src.domains.accounting.models.ledger import LedgerModel
from src.domains.accounting.models.journal import JournalEntryModel, JournalLineModel
import uuid

async def main():
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    print("Seeding Ledgers...")
    async with TestingSessionLocal() as session:
        LEDGER_NAMES = [
            "Sales - ShopDeck",
            "Sales Return - ShopDeck",
            "Razorpay Receivable",
            "ShopDeck Receivable",
            "Output CGST",
            "Output SGST",
            "Output IGST",
            "Round Off",
            "Axis Bank Current Account",
            "Payment Gateway Charges",
            "Input CGST",
            "Input SGST"
        ]
        ledgers = [LedgerModel(ledger_code=name.upper().replace(" ", "_"), ledger_name=name, account_type="REVENUE" if "Sales" in name else "ASSET") for name in LEDGER_NAMES]
        session.add_all(ledgers)
        await session.commit()
        
    print("Seeding Main Warehouse...")
    async with TestingSessionLocal() as session:
        warehouse_id = uuid.UUID("96c6b20c-d119-4f97-b635-c8e5ef87fd52")
        new_w = WarehouseModel(
            id=warehouse_id,
            warehouse_code="MAIN",
            warehouse_name="Main Warehouse",
            description="Default Main Warehouse",
            address_line_1="123 Main St",
            city="Delhi",
            state="Delhi",
            country="India",
            pin_code="110001"
        )
        session.add(new_w)
        await session.commit()

    print("Database reset complete.")

if __name__ == "__main__":
    asyncio.run(main())
