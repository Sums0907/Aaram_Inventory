import asyncio
import httpx
from jose import jwt
import time

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
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        res = await client.get("/api/v1/inventory/balances", headers=HEADERS)
        balances = res.json()["data"]
        sku_id = next((b["sku_id"] for b in balances if b["sku_code"] == "KD-RJ-RJP-KDB"), None)
        
        if sku_id:
            ledger_res = await client.get(f"/api/v1/inventory/ledger/{sku_id}", headers=HEADERS)
            ledger = ledger_res.json()["data"]
            print(f"Opening Balance: {ledger['opening_balance']}")
            print("Entries:")
            for e in ledger['entries']:
                m = e['movement']
                print(f"  {m['movement_date']} | {m['movement_type']:<20} | {m['quantity']:>5} | Running: {e['running_balance']}")
            print(f"Closing Balance: {ledger['closing_balance']}")

asyncio.run(main())
