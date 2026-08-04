import pytest
from pydantic import ValidationError
from src.domains.masters.schemas.product_attribute import ProductAttributeCreate, ProductAttributeUpdate

def test_product_attribute_create_valid():
    schema = ProductAttributeCreate(
        attribute_code="COL",
        attribute_name="Colour",
        description="Product colour",
        display_order=1
    )
    assert schema.attribute_code == "COL"
    assert schema.display_order == 1

def test_product_attribute_create_invalid_display_order():
    with pytest.raises(ValidationError):
        ProductAttributeCreate(
            attribute_code="COL",
            attribute_name="Colour",
            display_order=-5
        )

def test_product_attribute_update_omits_code():
    schema = ProductAttributeUpdate(
        attribute_name="Colour Updated",
        display_order=2
    )
    assert not hasattr(schema, "attribute_code")
    assert schema.attribute_name == "Colour Updated"
