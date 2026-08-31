import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import json

SQLITE_DB = "test_manual.db"
PG_DSN = "postgresql://postgres:password@localhost:5433/inventory_dev"

# Order matters for foreign keys
TABLES_ORDER = [
    "categories",
    "units_of_measure",
    "products",
    "skus",
    "masters_suppliers",
    "warehouses",
    "masters_boms",
    "masters_bom_items",
    "accounting_ledgers",
    "inventory_goods_receipts",
    "inventory_goods_receipt_items",
    "inventory_movements",
    "inventory_balances",
    "inventory_exceptions",
    "inventory_job_work_issues",
    "inventory_job_work_returns",
    "inventory_job_worker_stock",
    "inventory_transformation_register",
    "inventory_job_work_allocations",
    "jwa_job_work_rates",
    "jwa_job_work_expenses",
    "jwa_job_worker_payments",
    "jwa_payable_allocations",
    "system_sequences",
    "shopdeck_downloaded_reports"
]

def migrate():
    print("Starting migration from SQLite to Postgres...")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    pg_conn = psycopg2.connect(PG_DSN)
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Disable foreign key checks for this session
    pg_cursor.execute("SET session_replication_role = 'replica';")
    
    for table in TABLES_ORDER:
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            continue
            
        print(f"Migrating {len(rows)} rows for table: {table}")
        
        sqlite_cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in sqlite_cursor.fetchall()]
        
        pg_cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';")
        pg_types = {row[0]: row[1] for row in pg_cursor.fetchall()}
        
        col_names = ", ".join([f'"{c}"' for c in columns])
        
        processed_rows = []
        for row in rows:
            new_row = list(row)
            for i, col in enumerate(columns):
                val = new_row[i]
                pg_type = pg_types.get(col)
                
                if pg_type == 'boolean' and val in (0, 1):
                    new_row[i] = bool(val)
                    continue
                    
                if isinstance(val, str) and (val.startswith('{') or val.startswith('[')):
                    try:
                        new_row[i] = json.dumps(json.loads(val))
                    except:
                        pass
            processed_rows.append(tuple(new_row))
            
        insert_query = f"INSERT INTO {table} ({col_names}) VALUES %s ON CONFLICT DO NOTHING;"
        
        try:
            execute_values(pg_cursor, insert_query, processed_rows)
            pg_conn.commit()
            print(f"  -> Success: {table}")
        except Exception as e:
            pg_conn.rollback()
            print(f"  -> Error migrating {table}: {e}")
            
    # Re-enable foreign key checks
    pg_cursor.execute("SET session_replication_role = 'origin';")
    pg_conn.commit()
            
    sqlite_conn.close()
    pg_conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
