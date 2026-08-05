import asyncio
import httpx
from pathlib import Path
import os
import zipfile
import io
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.foundation.authentication.jwt import create_access_token

API_BASE_URL = "http://localhost:8000/api/v1"
INPUT_DIR = Path("tests/golden_dataset/input")
USER_ID = "00000000-0000-0000-0000-000000000000"

# Generate token
access_token = create_access_token({"sub": USER_ID, "username": "admin", "role": "SUPER_ADMIN"})
AUTH_HEADERS = {"Authorization": f"Bearer {access_token}"}

async def upload_file(client: httpx.AsyncClient, file_path: Path, platform: str, file_type: str, integration_id: str) -> str:
    endpoint_map = {
        "TAX_INVOICE": "shopdeck/tax-invoices",
        "SALES_ORDER": "shopdeck/orders",
        "COD_SETTLEMENT": "shopdeck/cod-settlements",
        "SETTLEMENT": "shopdeck/razorpay-settlements"
    }
    endpoint = endpoint_map[file_type]
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "text/csv")}
        
        response = await client.post(
            f"{API_BASE_URL}/data-ingestion/{endpoint}?integration_id={integration_id}",
            files=files,
            headers=AUTH_HEADERS
        )
        response.raise_for_status()
        return response.json()["data"]["id"]

async def main():
    from src.app.main import app
    from httpx import ASGITransport
    from dependency_injector import providers
    from src.foundation.database.session import Database
    
    # Override DB to use local sqlite test_manual.db
    TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"
    app.core_container.db.override(
        providers.Singleton(Database, db_url=TEST_DATABASE_URL, debug=False, pool_size=1, max_overflow=0)
    )
    
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        # Override the API_BASE_URL to point to local app
        global API_BASE_URL
        API_BASE_URL = "http://test/api/v1"
        
        print("Creating Integration...")
        
        # 0. Create Integration
        integration_data = {
            "integration_code": "SHOPDECK_TEST",
            "integration_name": "Shopdeck Account 1",
            "integration_type": "SHOPDECK"
        }
        integration_res = await client.post(f"{API_BASE_URL}/data-ingestion/integrations", json=integration_data, headers=AUTH_HEADERS)
        integration_res.raise_for_status()
        integration_id = integration_res.json()["data"]["id"]
        
        print("Uploading ShopDeck and Razorpay Reports...")
        
        # 1. Upload Reports
        tax_job = await upload_file(client, INPUT_DIR / "Tax Ready Report.csv", "SHOPDECK", "TAX_INVOICE", integration_id)
        order_job = await upload_file(client, INPUT_DIR / "Order Reconciliation Report.csv", "SHOPDECK", "SALES_ORDER", integration_id)
        cod_job = await upload_file(client, INPUT_DIR / "COD Settlement Report.csv", "SHOPDECK", "COD_SETTLEMENT", integration_id)
        razorpay_job = await upload_file(client, INPUT_DIR / "razorpay Settlement Reconciliation Report.csv", "RAZORPAY", "SETTLEMENT", integration_id)
        
        jobs = [tax_job, order_job, cod_job, razorpay_job]
        
        print("Processing Import Jobs...")
        
        # 2. Approve and Commit
        for job_id in jobs:
            approve_res = await client.post(f"{API_BASE_URL}/data-ingestion/import-jobs/{job_id}/approve", headers=AUTH_HEADERS)
            approve_res.raise_for_status()
            
            commit_res = await client.post(f"{API_BASE_URL}/data-ingestion/import-jobs/{job_id}/commit", headers=AUTH_HEADERS)
            commit_res.raise_for_status()

        print("Executing Pipeline (Matching & Accounting)...")
        # 3. Pipeline (Operations -> Matching -> Accounting)
        # Note: Since the orchestrator automatically fires event-driven jobs or is triggered by a cron/API, 
        # let's assume there's a trigger matching endpoint if it's not automated. 
        # The prompt says: Upload -> Approve -> Commit -> Matching -> Accounting.
        # But wait, in the AaramBooks architecture, pipeline orchestration happens via `/matching/jobs`
        
        match_res = await client.post(f"{API_BASE_URL}/matching/jobs", headers=AUTH_HEADERS)
        match_res.raise_for_status()
        
        print("Fetching Business Summary...")
        
        # 4. Fetch Dashboard Summary
        summary_res = await client.get(f"{API_BASE_URL}/dashboard/summary", headers=AUTH_HEADERS)
        summary_res.raise_for_status()
        summary = summary_res.json()["data"]
        
        print("Exporting Vyapar Journals...")
        
        # 5. Vyapar Export
        sales_export = await client.get(f"{API_BASE_URL}/accounting/export/vyapar/sales", headers=AUTH_HEADERS)
        sales_export.raise_for_status()
        
        cn_export = await client.get(f"{API_BASE_URL}/accounting/export/vyapar/credit-notes", headers=AUTH_HEADERS)
        cn_export.raise_for_status()
        
        settlement_export = await client.get(f"{API_BASE_URL}/accounting/export/vyapar/settlements", headers=AUTH_HEADERS)
        settlement_export.raise_for_status()
        
        export_status = "PASS" if all([sales_export.text, cn_export.text, settlement_export.text]) else "FAIL"
        
        # Print Final Output
        print("\n================================================")
        print("AARAMBOOKS VERSION 1 DEMO")
        print("================================================")
        print(f"Imported Records       {summary.get('Imported Records', 0)}")
        print(f"Sales Orders           {summary.get('Sales Orders', 0)}")
        print(f"Tax Invoices           {summary.get('Tax Invoices', 0)}")
        print(f"Payments               {summary.get('Payments', 0)}")
        print(f"Settlements            {summary.get('Settlements', 0)}")
        print(f"Matched Orders         {summary.get('Matched Orders', 0)}")
        print(f"Inventory Movements    {summary.get('Inventory Movements', 0)}")
        print(f"Journal Entries        {summary.get('Journal Entries', 0)}")
        print(f"Journal Lines          {summary.get('Journal Lines', 0)}")
        print(f"Golden Dataset         {summary.get('Golden Dataset Status', 'UNKNOWN')}")
        print(f"Verification           {summary.get('Golden Dataset Status', 'UNKNOWN')}")
        print(f"Vyapar Export          {export_status}")
        print("================================================\n")
        
if __name__ == "__main__":
    asyncio.run(main())
