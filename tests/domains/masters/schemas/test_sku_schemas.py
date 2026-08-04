import pytest
from uuid import uuid7
from pydantic import ValidationError
from src.domains.masters.schemas.sku import SKUCreate, SKUUpdate

def test_sku_create_valid():
    schema = SKUCreate(
        sku_code="SKU-1",
        sku_name="King Blue Bedsheet",
        inventory_item_id=uuid7(),
        attribute_values={"Size": "King", "Color": "Blue"},
        gst_rate=12.0
    )
    assert schema.sku_code == "SKU-1"
    assert schema.gst_rate == 12.0
    assert schema.attribute_values["Size"] == "King"

def test_sku_create_invalid_gst():
    with pytest.raises(ValidationError):
        SKUCreate(
            sku_code="SKU-1",
            sku_name="King Blue Bedsheet",
            inventory_item_id=uuid7(),
            attribute_values={"Size": "King"},
            gst_rate=-5.0 # Invalid
        )

def test_sku_update_omits_code_and_item():
    schema = SKUUpdate(
        sku_name="King Blue Bedsheet Updated",
        attribute_values={"Size": "King", "Color": "Dark Blue"},
        gst_rate=18.0
    )
    assert not hasattr(schema, "sku_code")
    assert not hasattr(schema, "inventory_item_id")
    assert schema.sku_name == "King Blue Bedsheet Updated"
