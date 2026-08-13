from sqlalchemy import text
from src.foundation.database.session import SessionLocal

def add_bom_name():
    with SessionLocal() as db:
        try:
            db.execute(text("ALTER TABLE masters_boms ADD COLUMN bom_name VARCHAR(255);"))
            db.commit()
            print("Column added successfully")
        except Exception as e:
            print(f"Error: {e}")

add_bom_name()
