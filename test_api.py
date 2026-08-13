import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import uuid
import httpx

async def test():
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/aarambooks")
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT id FROM warehouses LIMIT 1"))
        warehouse_id = str(res.scalar())
        
        res = await conn.execute(text("SELECT id FROM masters_suppliers WHERE supplier_type = 'JOB_WORKER' LIMIT 1"))
        supplier_id = str(res.scalar())
        
        res = await conn.execute(text("SELECT target_item_id FROM masters_boms LIMIT 1"))
        sku_id = str(res.scalar())
        
    print(warehouse_id, supplier_id, sku_id)
    
    async with httpx.AsyncClient() as client:
        res = await client.post("http://localhost:8000/api/v1/inventory/goods-receipts/", json={
            "supplier_id": supplier_id,
            "warehouse_id": warehouse_id,
            "receipt_date": "2026-08-11",
            "receipt_type": "JOB_WORK_RECEIPT",
            "grn_number": f"TEST-GRN-{uuid.uuid4().hex[:4]}",
            "items": [
                {
                    "sku_id": sku_id,
                    "quantity": 10
                }
            ]
        })
        print("Status", res.status_code)
        print("Response", res.json())

if __name__ == "__main__":
    asyncio.run(test())
