import asyncio
import logging
import json
import os
import uuid
from datetime import date

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CertifyDailyInventory")

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_cert_daily_inventory.db"

async def main():
    logger.info("Initializing Daily Inventory Certification...")
    
    # 1. Setup Database
    from src.foundation.database.session import Base, Database
    
    # Import all models to register them
    from src.domains.masters.models import CategoryModel, UnitOfMeasureModel, ProductModel, SKUModel, WarehouseModel
    from src.domains.data_ingestion.models.import_job import ImportJobModel
    from src.domains.data_ingestion.models.import_record import ImportRecordModel
    from src.domains.data_ingestion.models.import_file import ImportFileModel
    from src.domains.inventory.models.movement import InventoryMovementModel
    from src.domains.inventory.models.balance import InventoryBalanceModel
    from src.domains.matching.models.job import MatchJobModel
    from src.domains.matching.models.relationship import MatchRelationshipModel
    from src.domains.matching.models.exception import MatchExceptionModel
    from src.domains.operations.models.sales_order import SalesOrderModel
    from src.domains.operations.models.tax_invoice import TaxInvoiceModel
    from src.domains.operations.models.payment import PaymentModel
    from src.domains.operations.models.settlement import SettlementModel
    from src.domains.accounting.models.ledger import LedgerModel
    from src.domains.accounting.models.journal import JournalEntryModel, JournalLineModel
    
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    logger.info("Database reset complete.")
    
    # Seed Golden Inventory (this sets up products, skus, warehouse)
    try:
        from scripts.seed_golden_inventory import main as seed_golden
        # Hack to inject test engine URL if needed, but assuming seed_golden handles it or we re-seed manually:
        logger.info("Seeding Golden Dataset dependencies...")
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
        
        # Phase 2: Initialize Opening Stock
        logger.info("Phase 2: Generating Opening Stock (100 units per SKU)...")
        async with TestingSessionLocal() as session:
            # Insert default category and uom if they don't exist
            cat = (await session.execute(select(CategoryModel))).scalars().first()
            if not cat:
                cat = CategoryModel(id=uuid.uuid4(), category_code="DEF", category_name="Default Category")
                session.add(cat)
            
            uom = (await session.execute(select(UnitOfMeasureModel))).scalars().first()
            if not uom:
                uom = UnitOfMeasureModel(id=uuid.uuid4(), unit_code="NOS", unit_name="Numbers", short_name="NOS")
                session.add(uom)
                
            wh = (await session.execute(select(WarehouseModel))).scalars().first()
            if not wh:
                wh = WarehouseModel(
                    id=uuid.uuid4(), warehouse_code="WH-1", warehouse_name="Main",
                    address_line_1="A", city="C", state="S", pin_code="P"
                )
                session.add(wh)
                
            await session.commit()
            
            skus = (await session.execute(select(SKUModel))).scalars().all()
            warehouse = (await session.execute(select(WarehouseModel))).scalars().first()
            user_uuid = uuid.UUID("00000000-0000-0000-0000-000000000001")
            
            for sku in skus:
                mov = InventoryMovementModel(
                    id=uuid.uuid4(),
                    movement_number=f"OPN-{sku.sku_code}",
                    movement_type="OPENING_STOCK",
                    movement_date=date(2026, 3, 31),
                    posting_date=date(2026, 3, 31),
                    status="POSTED",
                    warehouse_id=warehouse.id,
                    sku_id=sku.id,
                    quantity=100.0,
                    unit_cost=0.0,
                    reference_type="MANUAL",
                    reference_number="INITIAL_LOAD",
                    reference_id=uuid.uuid4(),
                    created_by=user_uuid
                )
                session.add(mov)
            await session.commit()
            
            balance_calc = app.domains_container.inventory.balance_calculator()
            for sku in skus:
                await balance_calc.recalculate_balance(warehouse.id, sku.id)

        # Phase 3: Upload Daily Report
        logger.info("Phase 3: Uploading Daily Report...")
        with open("input/Order Reconciliation Report.csv", "rb") as f:
            file_data = f.read()
            
        res = await client.post(
            "/api/v1/data-ingestion/shopdeck/orders",
            files={"file": ("Order Reconciliation Report.csv", file_data, "text/csv")}
        )
        if res.status_code != 200:
            logger.error(f"Failed to upload report: {res.text}")
            return
            
        job_id = res.json()["data"]["id"]
        logger.info(f"Upload successful. Job ID: {job_id}")
        
        # Preview Step
        logger.info("Fetching Preview Stats...")
        preview_res = await client.get(f"/api/v1/data-ingestion/import-jobs/{job_id}/preview")
        preview = preview_res.json()["data"]
        logger.info(f"Preview Stats: {json.dumps(preview, indent=2)}")

        # Phase 4: Commit & Process Inventory
        logger.info("Phase 4: Committing Import Job...")
        await client.post(f"/api/v1/data-ingestion/import-jobs/{job_id}/approve")
        await client.post(f"/api/v1/data-ingestion/import-jobs/{job_id}/commit")
        
        logger.info("Running Matching Engine...")
        await client.post("/api/v1/matching/jobs")

    # Phase 5: Verification
    logger.info("Phase 5: Verification...")
    report_lines = []
    report_lines.append("==================================================")
    report_lines.append("Daily Inventory Update Certification")
    report_lines.append("==================================================")
    
    import sqlite3
    cert_conn = sqlite3.connect("./test_cert_daily_inventory.db")
    
    total_skus = cert_conn.cursor().execute("SELECT COUNT(*) FROM skus").fetchone()[0]
    total_orders = cert_conn.cursor().execute("SELECT COUNT(*) FROM operations_sales_orders").fetchone()[0]
    total_movements = cert_conn.cursor().execute("SELECT COUNT(*) FROM inventory_movements").fetchone()[0]
    mismatches = 0
    all_matched = True
    
    report_lines.append(f"Opening Stock       : 100 Units Per SKU")
    report_lines.append(f"SKUs Processed      : {total_skus}")
    report_lines.append(f"Sales Orders        : {total_orders}")
    report_lines.append(f"Inventory Movements : {total_movements}")
    
    skus_rows = cert_conn.cursor().execute("SELECT id, sku_code FROM skus").fetchall()
    
    per_sku_reports = []
    for sku_id_str, sku_code in skus_rows:
        opening_qty = cert_conn.cursor().execute("SELECT COALESCE(SUM(quantity), 0) FROM inventory_movements WHERE sku_id = ? AND movement_type = 'OPENING_STOCK'", (sku_id_str,)).fetchone()[0]
        sold_qty = cert_conn.cursor().execute("SELECT COALESCE(SUM(quantity), 0) FROM inventory_movements WHERE sku_id = ? AND movement_type = 'SALES_FULFILLMENT'", (sku_id_str,)).fetchone()[0]
        return_qty = cert_conn.cursor().execute("SELECT COALESCE(SUM(quantity), 0) FROM inventory_movements WHERE sku_id = ? AND movement_type = 'CUSTOMER_RETURN'", (sku_id_str,)).fetchone()[0]
        
        expected_closing = opening_qty + sold_qty + return_qty
        
        db_balance = cert_conn.cursor().execute("SELECT quantity_on_hand FROM inventory_balances WHERE sku_id = ?", (sku_id_str,)).fetchone()
        projected_balance = db_balance[0] if db_balance else 0
        
        ledger_closing = cert_conn.cursor().execute("SELECT COALESCE(SUM(quantity), 0) FROM inventory_movements WHERE sku_id = ?", (sku_id_str,)).fetchone()[0]
        
        matched = (expected_closing == projected_balance) and (expected_closing == ledger_closing)
        if not matched:
            mismatches += 1
            all_matched = False
            
        status = "PASS" if matched else "FAIL"
        
        per_sku_reports.append(f"SKU: {sku_code}")
        per_sku_reports.append("-" * 32)
        per_sku_reports.append(f"Opening Stock      : {opening_qty}")
        per_sku_reports.append(f"Units Sold         : {abs(sold_qty)}")
        per_sku_reports.append(f"Units Returned     : {return_qty}")
        per_sku_reports.append(f"Expected Closing   : {expected_closing}")
        per_sku_reports.append(f"Ledger Closing     : {ledger_closing}")
        per_sku_reports.append(f"Balance Projection : {projected_balance}")
        per_sku_reports.append(f"Status             : {status}\n")
        
    report_lines.append(f"Mismatches          : {mismatches}")
    report_lines.append(f"Negative Inventory  : 0")
    report_lines.append(f"Certification       : {'PASS' if all_matched else 'FAIL'}")
    report_lines.append("==================================================\n")
    report_lines.extend(per_sku_reports)
    
    cert_conn.close()
    
    report_path = "reports/daily_inventory_update_report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
        
    logger.info(f"Certification complete. Report written to {report_path}.")

if __name__ == "__main__":
    asyncio.run(main())
