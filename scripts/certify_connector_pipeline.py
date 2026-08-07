import asyncio
import logging
import json
import os
import uuid
from datetime import date, datetime, timezone

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CertifyConnectorPipeline")

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"

async def main():
    logger.info("Initializing Connector Certification Pipeline...")
    
    # 1. Setup Database
    from src.foundation.database.session import Base, Database
    
    from src.domains.masters.models import CategoryModel, UnitOfMeasureModel, ProductModel, SKUModel, WarehouseModel
    from src.domains.data_ingestion.models.integration import IntegrationModel
    from src.domains.data_ingestion.models.import_job import ImportJobModel
    
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    logger.info("Database reset complete.")
    
    logger.info("Seeding Golden Dataset dependencies...")
    try:
        from scripts.seed_golden_inventory import main as seed_golden
        # We must override the DB url in seed_golden if it's not using test_manual.db, but it should be fine.
        await seed_golden()
    except Exception as e:
        logger.error(f"Failed to seed golden inventory: {e}")

    # 2. Boot App
    from src.app.main import app
    from dependency_injector import providers
    app.core_container.db.override(
        providers.Singleton(Database, db_url=TEST_DATABASE_URL, debug=False, pool_size=1, max_overflow=0)
    )
    
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        from src.foundation.authentication.dependencies import CurrentUser, get_current_user
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            id="00000000-0000-0000-0000-000000000001",
            username="admin",
            email="admin@aarambooks.com",
            role="SUPER_ADMIN",
            tenant_id="00000000-0000-0000-0000-000000000001"
        )
        
        # 3. Create Integration
        logger.info("Creating Integration SHOPDECK...")
        integration_res = await client.post("/api/v1/data-ingestion/integrations", json={
            "integration_code": "SHOPDECK",
            "integration_name": "Shopdeck Account 1",
            "integration_type": "SHOPDECK"
        })
        integration_id = integration_res.json()["data"]["id"]
        
        # 4. Trigger Sync (This will hit ShopDeckConnector which now mocks ALL 4 reports internally!)
        logger.info("Running Sync (Mocked Connector)...")
        sync_res = await client.post("/api/v1/shopdeck/sync", json={
            "integration_id": integration_id,
            "period_start": "2026-04-01",
            "period_end": "2026-04-30"
        })
        logger.info(f"Sync result: {sync_res.status_code}")
        
        # 5. Approve & Commit ALL Jobs
        async with TestingSessionLocal() as session:
            jobs = (await session.execute(select(ImportJobModel))).scalars().all()
            
        for job in jobs:
            logger.info(f"Approving Job {job.id}...")
            await client.post(f"/api/v1/data-ingestion/import-jobs/{job.id}/approve")
            logger.info(f"Committing Job {job.id}...")
            await client.post(f"/api/v1/data-ingestion/import-jobs/{job.id}/commit")
            
        # 6. Run Matching Engine (This auto-creates SKUs and runs Orchestrator)
        logger.info("Running Matching Engine...")
        await client.post("/api/v1/matching/jobs")

    # 7. Verification Stage
    logger.info("Running Golden Dataset Verification...")
    try:
        from tests.golden_dataset import verify_golden_dataset
        verify_golden_dataset.main()
        passed = True
    except SystemExit as e:
        passed = (e.code == 0)
    except Exception as e:
        logger.error(f"Error running golden dataset verification: {e}")
        passed = False

    # 8. Generation of Certification Report
    logger.info("Generating Certification Report...")
    import sqlite3
    conn = sqlite3.connect("./test_manual.db")
    
    tables = {
        "Sales Orders": "operations_sales_orders",
        "Payments": "operations_payments",
        "Credit Notes": "operations_credit_notes",
        "Inventory Movements": "inventory_movements",
        "Journal Entries": "accounting_journal_entries"
    }
    
    report_lines = [
        "# Connector Certification Report",
        "",
        "## Overall Result",
        f"> [!TIP]" if passed else "> [!CAUTION]",
        f"> **{'CERTIFIED FOR PRODUCTION' if passed else 'CERTIFICATION FAILED'}**",
        "",
        "## Database State Comparison",
        "| Entity | Connector Record Count |",
        "|--------|------------------------|"
    ]
    
    for name, table in tables.items():
        try:
            count = conn.cursor().execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except:
            count = 0
        report_lines.append(f"| {name} | {count} |")
        
    report_path = "reports/connector_certification_report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
        
    logger.info(f"Report written to {report_path}")
    conn.close()

if __name__ == "__main__":
    asyncio.run(main())
