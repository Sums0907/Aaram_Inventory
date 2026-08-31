import urllib.request
import json
import psycopg2
import sqlite3

def print_table(data):
    if not data:
        print("No SKUs found.")
        return
    keys = data[0].keys()
    print("| " + " | ".join(keys) + " |")
    print("|" + "|".join(["---"] * len(keys)) + "|")
    for row in data:
        print("| " + " | ".join(str(row.get(k, '')) for k in keys) + " |")

print("=== API SKUs (http://127.0.0.1:8100/api/v1/skus) ===")
api_success = False
try:
    req = urllib.request.Request("http://127.0.0.1:8100/api/v1/skus")
    with urllib.request.urlopen(req, timeout=1) as response:
        data = json.loads(response.read().decode())
        # API often wraps it in a data field or similar
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        print_table(data)
        api_success = True
except Exception as e:
    print("API Failed or timed out (Server not running locally):", type(e).__name__)
    
if not api_success:
    print("\n=== Postgres SKUs (inventory_dev) ===")
    try:
        conn = psycopg2.connect("postgresql://postgres:password@localhost:5433/inventory_dev", connect_timeout=2)
        cur = conn.cursor()
        cur.execute("SELECT sku_code, item_code, status FROM skus LIMIT 50;")
        rows = cur.fetchall()
        if not rows:
            print("No SKUs found in Postgres inventory_dev database.")
        else:
            cols = [desc[0] for desc in cur.description]
            data = [dict(zip(cols, row)) for row in rows]
            print_table(data)
    except Exception as db_e:
        print("Database query failed:", type(db_e).__name__)

    print("\n=== SQLite SKUs (test_manual.db) ===")
    try:
        conn = sqlite3.connect("test_manual.db")
        cur = conn.cursor()
        cur.execute("SELECT sku_code, item_code, status FROM skus LIMIT 50;")
        rows = cur.fetchall()
        if not rows:
            print("No SKUs found in test_manual.db.")
        else:
            cols = [desc[0] for desc in cur.description]
            data = [dict(zip(cols, row)) for row in rows]
            print_table(data)
    except Exception as e:
        print("SQLite query failed:", type(e).__name__)
