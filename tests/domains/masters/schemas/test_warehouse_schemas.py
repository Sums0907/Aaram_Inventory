import pytest
from pydantic import ValidationError
from src.domains.masters.schemas.warehouse import WarehouseCreate, WarehouseUpdate

def test_warehouse_create_valid():
    schema = WarehouseCreate(
        warehouse_code="DEL-01",
        warehouse_name="Delhi Hub",
        address_line_1="123 Main St",
        city="New Delhi",
        state="Delhi",
        pin_code="110001",
        email="hub@example.com"
    )
    assert schema.warehouse_code == "DEL-01"
    assert schema.country == "India" # Default value

def test_warehouse_create_invalid_email():
    with pytest.raises(ValidationError):
        WarehouseCreate(
            warehouse_code="DEL-01",
            warehouse_name="Delhi Hub",
            address_line_1="123 Main St",
            city="New Delhi",
            state="Delhi",
            pin_code="110001",
            email="invalid-email"
        )

def test_warehouse_update_omits_code():
    schema = WarehouseUpdate(
        warehouse_name="Delhi Hub Updated",
        address_line_1="123 Main St",
        city="New Delhi",
        state="Delhi",
        pin_code="110001"
    )
    assert not hasattr(schema, "warehouse_code")
    assert schema.warehouse_name == "Delhi Hub Updated"
