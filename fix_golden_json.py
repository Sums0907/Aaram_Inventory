import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.domains.accounting.services.aggregation import JournalAggregationService
import pandas as pd
from pathlib import Path
import json

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

BASE_DIR = Path(__file__).parent
EXPECTED_DIR = BASE_DIR / "tests" / "golden_dataset" / "expected"

async def main():
    async with TestingSessionLocal() as session:
        service = JournalAggregationService(session)
        sales_df = await service.aggregate_sales_journal()
        credit_df = await service.aggregate_credit_note_journal()
        settlement_df = await service.aggregate_settlement_journal()
        
        with open(EXPECTED_DIR / "golden_sales_journal.json", "w") as f:
            json.dump(sales_df.to_dict(orient="records"), f, indent=4)
            
        with open(EXPECTED_DIR / "golden_credit_note_journal.json", "w") as f:
            json.dump(credit_df.to_dict(orient="records"), f, indent=4)
            
        with open(EXPECTED_DIR / "golden_settlement_journal.json", "w") as f:
            json.dump(settlement_df.to_dict(orient="records"), f, indent=4)
            
        print("Updated Golden JSONs successfully.")

if __name__ == "__main__":
    asyncio.run(main())
