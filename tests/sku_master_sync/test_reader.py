import pytest
from src.domains.sku_master_sync.shopdeck_reader import ShopDeckReader

def test_reader_parses_valid_csv():
    csv_content = """Sku Id,Product Code,Name,Selling Price,Quantity,Category Path
10001,BED-001,Blue Bedsheet,1499.00,50,Home
10002,BED-002,Red Bedsheet,1599.00,20,Home
"""
    rows = ShopDeckReader.parse_csv(csv_content)
    assert len(rows) == 2
    assert rows[0]["shopdeck_sku_id"] == "10001"
    assert rows[0]["product_code"] == "BED-001"
    assert rows[0]["selling_price"] == 1499.0
    
def test_reader_ignores_quantity():
    csv_content = """Sku Id,Product Code,Name,Selling Price,Quantity
10001,BED-001,Blue Bedsheet,1499.00,5000
"""
    rows = ShopDeckReader.parse_csv(csv_content)
    assert "Quantity" not in rows[0]
    assert "quantity" not in rows[0]

def test_reader_missing_essential_columns():
    csv_content = """Product Code,Name
BED-001,Blue Bedsheet
"""
    with pytest.raises(ValueError, match="Missing required columns"):
        ShopDeckReader.parse_csv(csv_content)
