import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
EXPECTED_DIR = BASE_DIR / "tests" / "golden_dataset" / "expected"
DB_PATH = BASE_DIR / "test_manual.db"

EXPECTED_DIR.mkdir(parents=True, exist_ok=True)

def dump_table(cursor, table_name, file_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        data.append(row_dict)
        
    with open(EXPECTED_DIR / file_name, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Dumped {len(data)} rows to {file_name}")

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables_to_dump = {
        "operations_sales_orders": "sales_orders.json",
        "operations_tax_invoices": "tax_invoices.json",
        "operations_payments": "payments.json",
        "operations_settlements": "settlements.json",
        "inventory_movements": "inventory_movements.json",
        "accounting_journal_entries": "journal_entries.json",
        "accounting_journal_lines": "journal_lines.json"
        # We don't have inventory_balances table currently, we calculate it dynamically usually, or we can skip it if it's 0.
    }
    
    for table, file_name in tables_to_dump.items():
        try:
            dump_table(cursor, table, file_name)
        except sqlite3.OperationalError as e:
            print(f"Skipping {table}: {e}")
            
    conn.close()

if __name__ == "__main__":
    main()
