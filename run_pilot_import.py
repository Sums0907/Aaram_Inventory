import asyncio
import httpx
from jose import jwt
import time
import uuid

secret = "super-secret-key-change-in-production"
payload = {
    "sub": "00000000-0000-0000-0000-000000000001",
    "username": "admin",
    "role": "SUPER_ADMIN",
    "exp": int(time.time()) + 3600
}
TOKEN = jwt.encode(payload, secret, algorithm="HS256")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

async def main():
    print("Uploading Order Reconciliation Report to local backend...")
    
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=120.0) as client:
        with open("input/Order Reconciliation Report.csv", "rb") as f:
            file_data = f.read()
            
        print("-> POST /api/v1/data-ingestion/shopdeck/orders")
        res = await client.post(
            "/api/v1/data-ingestion/shopdeck/orders",
            files={"file": ("Order Reconciliation Report.csv", file_data, "text/csv")},
            headers=HEADERS
        )
        if res.status_code != 200:
            print(f"Failed to upload report: {res.text}")
            return
            
        job_id = res.json()["data"]["id"]
        print(f"Upload successful. Job ID: {job_id}")
        
        print("-> GET Preview Stats...")
        preview_res = await client.get(f"/api/v1/data-ingestion/import-jobs/{job_id}/preview", headers=HEADERS)
        preview = preview_res.json()["data"]
        print(f"Preview Stats: {preview}")

        print("-> POST Approve & Commit...")
        await client.post(f"/api/v1/data-ingestion/import-jobs/{job_id}/approve", headers=HEADERS)
        commit_res = await client.post(f"/api/v1/data-ingestion/import-jobs/{job_id}/commit", headers=HEADERS)
        print(f"Commit Status: {commit_res.status_code}")
        
        print("-> POST Trigger Truth Engine Matching...")
        match_res = await client.post("/api/v1/matching/jobs", headers=HEADERS)
        print(f"Matching Trigger Status: {match_res.status_code}")
        
        print("\nChecking final inventory balance for KD-RJ-RJP-KDB...")
        balances_res = await client.get("/api/v1/inventory/balances", headers=HEADERS)
        balances = balances_res.json()["data"]
        
        target_sku = [b for b in balances if b["sku_code"] == "KD-RJ-RJP-KDB"]
        if target_sku:
            print(f"\nFinal Balance for KD-RJ-RJP-KDB: {target_sku[0]['balance']} Units")
        else:
            print("SKU KD-RJ-RJP-KDB not found in balances.")

if __name__ == "__main__":
    asyncio.run(main())
