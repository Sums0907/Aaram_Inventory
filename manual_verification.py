import asyncio
import uuid
import sys
import logging
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ManualVerification")

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"

async def main():
    logger.info("Initializing Manual Verification...")
    
    # 1. Setup Database
    from src.foundation.database.session import Base, Database
    
    # Import all models to register them with Base.metadata
    from src.domains.masters.models import CategoryModel, UnitOfMeasureModel, ProductAttributeModel, InventoryItemModel, SKUModel, CompanyModel, WarehouseModel
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
    
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Boot App
    from src.app.main import app
    from dependency_injector import providers
    app.core_container.db.override(
        providers.Singleton(Database, db_url=TEST_DATABASE_URL, debug=False, pool_size=1, max_overflow=0)
    )
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create user (auth is mocked in current dependencies? wait, let's inject a current_user or use the default token if auth is enabled)
        # Auth middleware is active? If yes, we need to bypass or get token.
        # But wait, in tests, get_current_user returns a default user if we override the dependency!
        from src.foundation.authentication.dependencies import CurrentUser, get_current_user
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            id="00000000-0000-0000-0000-000000000001",
            username="admin",
            email="admin@aarambooks.com",
            role="SUPER_ADMIN",
            tenant_id="00000000-0000-0000-0000-000000000001"
        )
        
        # 3. Create Integration
        logger.info("Creating Test Integration...")
        integration_res = await client.post("/api/v1/data-ingestion/integrations", json={
            "integration_code": "SHOPDECK_TEST",
            "integration_name": "Shopdeck Account 1",
            "integration_type": "SHOPDECK"
        })
        if integration_res.status_code != 201:
            logger.error(f"Failed to create integration: {integration_res.text}")
            return
        
        integration_id = integration_res.json()["data"]["id"]
        logger.info(f"Integration Created: {integration_id}")
        
        # 4. Upload Files
        files_to_upload = [
            ("Order Reconciliation Report.csv", "/api/v1/data-ingestion/shopdeck/orders", "SHOPDECK_ORDERS"),
            ("Tax Ready Report.csv", "/api/v1/data-ingestion/shopdeck/tax-invoices", "SHOPDECK_TAX"),
            ("COD Settlement Report.csv", "/api/v1/data-ingestion/shopdeck/cod-settlements", "SHOPDECK_COD_SETTLEMENT"),
            ("razorpay Settlement Reconciliation Report.csv", "/api/v1/data-ingestion/shopdeck/razorpay-settlements", "RAZORPAY_SETTLEMENT")
        ]
        
        for filename, url, job_type in files_to_upload:
            filepath = f"input/{filename}"
            logger.info(f"Processing File: {filepath} to {url}")
            
            try:
                with open(filepath, "rb") as f:
                    file_content = f.read()
            except FileNotFoundError:
                logger.error(f"File not found: {filepath}")
                continue
                
            upload_res = await client.post(
                url, 
                params={"integration_id": integration_id},
                files={"file": (filename, file_content, "text/csv")}
            )
            
            if upload_res.status_code != 200 and upload_res.status_code != 201:
                logger.error(f"Failed to upload {filename}: {upload_res.text}")
                continue
                
            job_id = upload_res.json()["data"]["id"]
            logger.info(f"Import Job Created: {job_id}")
            
            # 5. Approve & Commit
            logger.info(f"Approving Job {job_id}...")
            approve_res = await client.post(f"/api/v1/data-ingestion/import-jobs/{job_id}/approve")
            if approve_res.status_code != 200:
                logger.error(f"Failed to approve job {job_id}: {approve_res.text}")
                
            logger.info(f"Committing Job {job_id}...")
            commit_res = await client.post(f"/api/v1/data-ingestion/import-jobs/{job_id}/commit")
            if commit_res.status_code != 200:
                logger.error(f"Failed to commit job {job_id}: {commit_res.text}")
                
        # 6. Run Matching Engine
        logger.info("=== Running Matching Engine ===")
        matching_res = await client.post("/api/v1/matching/jobs")
        if matching_res.status_code == 201:
            match_data = matching_res.json()["data"]
            logger.info(f"Matching Job Completed: {match_data['id']}")
            logger.info(f"Successful Matches: {match_data['successful_matches']}")
            logger.info(f"Exceptions Generated: {match_data['exceptions_generated']}")
        else:
            logger.error(f"Failed to run matching job: {matching_res.text}")
                
    # 7. Database Verification
    logger.info("=== Database Verification ===")
    async with TestingSessionLocal() as session:
        # Check Import Records
        valid_records = await session.execute(text("SELECT COUNT(*) FROM import_records WHERE status = 'VALID'"))
        logger.info(f"Import Records (VALID): {valid_records.scalar()}")
        
        invalid_records = await session.execute(text("SELECT COUNT(*) FROM import_records WHERE status = 'INVALID'"))
        logger.info(f"Import Records (INVALID): {invalid_records.scalar()}")
        
        committed_records = await session.execute(text("SELECT COUNT(*) FROM import_records WHERE status = 'COMMITTED'"))
        logger.info(f"Import Records (COMMITTED): {committed_records.scalar()}")
        
        failed_records = await session.execute(text("SELECT COUNT(*) FROM import_records WHERE status = 'FAILED_COMMIT'"))
        logger.info(f"Import Records (FAILED_COMMIT): {failed_records.scalar()}")
        
        # Check Operations tables
        sales_orders = await session.execute(text("SELECT COUNT(*) FROM operations_sales_orders"))
        logger.info(f"Sales Orders Created: {sales_orders.scalar()}")
        
        tax_invoices = await session.execute(text("SELECT COUNT(*) FROM operations_tax_invoices"))
        logger.info(f"Tax Invoices Created: {tax_invoices.scalar()}")
        
        settlements = await session.execute(text("SELECT COUNT(*) FROM operations_settlements"))
        logger.info(f"Settlements Created: {settlements.scalar()}")
        
        payments = await session.execute(text("SELECT COUNT(*) FROM operations_payments"))
        logger.info(f"Payments Created: {payments.scalar()}")
        
        # Check Matching tables
        matched_invoices = await session.execute(text("SELECT COUNT(*) FROM operations_tax_invoices WHERE order_id IS NOT NULL"))
        logger.info(f"Invoices Matched to Orders: {matched_invoices.scalar()}")
        
        matched_payments = await session.execute(text("SELECT COUNT(*) FROM operations_payments WHERE settlement_id IS NOT NULL"))
        logger.info(f"Payments Matched to Settlements: {matched_payments.scalar()}")

if __name__ == "__main__":
    asyncio.run(main())
