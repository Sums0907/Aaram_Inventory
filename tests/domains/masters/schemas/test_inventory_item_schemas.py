import pytest
from uuid_extensions import uuid7
from pydantic import ValidationError
from src.domains.masters.schemas.inventory_item import InventoryItemCreate, InventoryItemUpdate

def test_inventory_item_create_valid():
    schema = InventoryItemCreate(
        item_code="ITM-1",
        item_name="Bedsheet Deluxe",
        category_id=uuid7(),
        unit_of_measure_id=uuid7(),
        gst_rate=12.5,
        product_attribute_ids=[uuid7(), uuid7()]
    )
    assert schema.item_code == "ITM-1"
    assert schema.gst_rate == 12.5
    assert len(schema.product_attribute_ids) == 2

def test_inventory_item_create_invalid_gst():
    with pytest.raises(ValidationError):
        InventoryItemCreate(
            item_code="ITM-1",
            item_name="Bedsheet Deluxe",
            category_id=uuid7(),
            unit_of_measure_id=uuid7(),
            gst_rate=-5.0 # Invalid
        )

def test_inventory_item_update_omits_code():
    schema = InventoryItemUpdate(
        item_name="Bedsheet Premium",
        category_id=uuid7(),
        unit_of_measure_id=uuid7(),
        gst_rate=18.0
    )
    assert not hasattr(schema, "item_code")
    assert schema.item_name == "Bedsheet Premium"
