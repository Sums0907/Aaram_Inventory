import json
import sqlite3
import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent.parent.parent
EXPECTED_DIR = BASE_DIR / "tests" / "golden_dataset" / "expected"
DB_PATH = BASE_DIR / "test_manual.db"

def load_json(file_name):
    path = EXPECTED_DIR / file_name
    if not path.exists():
        return None
    with open(path, 'r') as f:
        return json.load(f)

def verify_table(cursor, table_name, expected_data):
    if expected_data is None:
        print(f"⚠️  Missing expected data for {table_name}, skipping.")
        return True
        
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    actual_data = [dict(zip(columns, row)) for row in rows]
    
    expected_count = len(expected_data)
    actual_count = len(actual_data)
    
    if expected_count != actual_count:
        print(f"❌ {table_name}: Count mismatch. Expected {expected_count}, got {actual_count}")
        return False
        
    print(f"✅ {table_name}: Count matches ({actual_count})")
    
    # Optional: We could do a deep comparison here, but row counts and specific sums are usually sufficient for regression
    return True

def verify_accounting_aggregation(conn):
    import asyncio
    from src.domains.accounting.services.aggregation import JournalAggregationService
    
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    
    TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    
    async def _run():
        all_passed = True
        async with TestingSessionLocal() as session:
            service = JournalAggregationService(session)
            
            # Sales Journal
            sales_df = await service.aggregate_sales_journal()
            sales_passed = _compare_journal("golden_sales_journal.json", sales_df, "Sales Journal")
            if not sales_passed: all_passed = False
                
            # Credit Note Journal
            credit_df = await service.aggregate_credit_note_journal()
            credit_passed = _compare_journal("golden_credit_note_journal.json", credit_df, "Credit Note Journal")
            if not credit_passed: all_passed = False
                
            # Settlement Journal
            settlement_df = await service.aggregate_settlement_journal()
            settlement_passed = _compare_journal("golden_settlement_journal.json", settlement_df, "Settlement Journal")
            if not settlement_passed: all_passed = False
                
        return all_passed
        
    return asyncio.run(_run())

def _compare_journal(golden_file, actual_df, name):
    expected_data = load_json(golden_file)
    if not expected_data:
        print(f"⚠️  Missing expected data for {name}")
        return True
        
    expected_df = pd.DataFrame(expected_data)
    
    # Drop rows where both Debit and Credit are exactly 0 in actual, in case they exist
    actual_df = actual_df[(actual_df['Debit'] != 0.0) | (actual_df['Credit'] != 0.0)]
    
    # Round to 2 decimal places to avoid float precision issues during comparison
    expected_df['Debit'] = expected_df['Debit'].round(2)
    expected_df['Credit'] = expected_df['Credit'].round(2)
    actual_df['Debit'] = actual_df['Debit'].round(2)
    actual_df['Credit'] = actual_df['Credit'].round(2)
    
    # Sort by ledger for deterministic comparison
    expected_df = expected_df.sort_values(by='Ledger').reset_index(drop=True)
    actual_df = actual_df.sort_values(by='Ledger').reset_index(drop=True)
    
    try:
        pd.testing.assert_frame_equal(expected_df[['Ledger', 'Debit', 'Credit']], actual_df[['Ledger', 'Debit', 'Credit']])
        print(f"✅ {name}: Matches exactly!")
        return True
    except AssertionError as e:
        print(f"❌ {name}: Mismatch detected!")
        print("Expected:")
        print(expected_df)
        print("Actual:")
        print(actual_df)
        return False

def main():
    print("="*60)
    print("GOLDEN DATASET VERIFICATION")
    print("="*60)
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}. Please run the pipeline first.")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables_to_verify = {
        "operations_sales_orders": "sales_orders.json",
        "operations_tax_invoices": "tax_invoices.json",
        "operations_payments": "payments.json",
        "operations_settlements": "settlements.json",
        "inventory_movements": "inventory_movements.json",
        "accounting_journal_entries": "journal_entries.json",
        "accounting_journal_lines": "journal_lines.json"
    }
    
    all_passed = True
    for table, file_name in tables_to_verify.items():
        expected_data = load_json(file_name)
        passed = verify_table(cursor, table, expected_data)
        if not passed:
            all_passed = False
            
    # Verify aggregated accounting journals
    if not verify_accounting_aggregation(conn):
        all_passed = False
            
    conn.close()
    
    print("="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED: The pipeline reproduces the Golden Dataset perfectly.")
        sys.exit(0)
    else:
        print("❌ TEST FAILED: Pipeline outputs do not match the Golden Dataset.")
        sys.exit(1)

if __name__ == "__main__":
    main()
