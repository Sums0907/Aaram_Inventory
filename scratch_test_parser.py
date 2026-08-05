import asyncio
import os
from uuid import uuid4
from src.app.container import DomainsContainer
from src.foundation.dependency_injection import CoreContainer

async def run_test():
    core = CoreContainer()
    core.config.from_dict({
        "database": {
            "url": "postgresql+asyncpg://postgres:postgres@db:5432/aarambooks",
            "pool_size": 5,
            "max_overflow": 10
        },
        "cors": {"allow_origins": ["*"]}
    })
    
    await core.init_resources()
    
    domains = DomainsContainer(core=core)
    
    adapter = domains.data_ingestion.shopdeck_order_adapter()
    
    file_path = "/app/input/Order Reconciliation Report.csv"
    
    with open(file_path, "rb") as f:
        file_content = f.read()
        
    print(f"Read {len(file_content)} bytes. Running adapter...")
    
    job_id = uuid4()
    user_id = uuid4()
    
    try:
        await adapter.parse_and_ingest(file_content, job_id, user_id)
        print("Successfully parsed and ingested!")
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
