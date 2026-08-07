import sqlite3

def migrate():
    conn = sqlite3.connect("test_manual.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN item_type VARCHAR(50) DEFAULT 'FINISHED_GOODS' NOT NULL")
        conn.commit()
        print("Migration successful: added item_type to products")
    except Exception as e:
        print(f"Error migrating: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
