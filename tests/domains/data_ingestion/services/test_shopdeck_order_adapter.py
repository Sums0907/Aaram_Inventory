import pytest
from uuid import uuid4
from src.domains.data_ingestion.services.adapters.shopdeck_order import ShopDeckOrderReader, ShopDeckOrderMapper, ShopDeckOrderValidator

def test_partial_cod_orders_are_included():
    # Mock CSV content with a PARTIAL-COD order
    csv_content = b"""Order Reconciliation Report
Date Range: 01/04/2026 to 30/04/2026
Order ID,Order Creation Date,Channel,Order Status,Customer Name,Payment Method,Invoice Total (Incl. Tax),SKU Code,Quantity,Product Amount (Incl. Tax),Product Tax Amount
NS0A7F1D2261B68230,01-04-2026,WEB,DELIVERED,John Doe,PARTIAL-COD,1249.00,KD-RJ-RJP-KDB,1,1249.00,59.48
NS064787FAB92464BF,01-04-2026,WEB,DELIVERED,Jane Doe,ONLINE,1149.00,KD-RJ-RJP-KDB,1,1149.00,54.71
"""
    
    # 1. Read
    reader = ShopDeckOrderReader()
    grouped_raw_list = reader.read(csv_content)
    
    assert len(grouped_raw_list) == 2, "Both orders should be read from the CSV"
    
    # 2. Validate & Map
    validator = ShopDeckOrderValidator()
    mapper = ShopDeckOrderMapper()
    
    parsed_orders = []
    for grouped_raw in grouped_raw_list:
        errors = validator.validate(grouped_raw)
        assert len(errors) == 0, "No validation errors expected"
        
        normalized = mapper.map(grouped_raw)
        parsed_orders.append(normalized)
        
    # 3. Assert
    assert len(parsed_orders) == 2, "Both orders should be mapped successfully"
    
    partial_cod_order = next(o for o in parsed_orders if o["external_order_id"] == "NS0A7F1D2261B68230")
    assert partial_cod_order["payment_method"] == "PARTIAL-COD", "Payment method should be preserved exactly as PARTIAL-COD"
    assert partial_cod_order["gross_amount"] == 1249.00, "Gross amount must be accurately extracted"
    
    online_order = next(o for o in parsed_orders if o["external_order_id"] == "NS064787FAB92464BF")
    assert online_order["payment_method"] == "ONLINE", "ONLINE payment method should be preserved"
