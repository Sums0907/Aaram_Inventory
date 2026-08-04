import pytest
from pydantic import ValidationError
from src.domains.masters.schemas.category import CategoryCreate, CategoryUpdate

def test_category_create_valid():
    schema = CategoryCreate(
        category_code="BED",
        category_name="Bedsheet",
        description="Premium Bedsheets",
        display_order=1
    )
    assert schema.category_code == "BED"
    assert schema.display_order == 1

def test_category_create_invalid_display_order():
    with pytest.raises(ValidationError):
        CategoryCreate(
            category_code="BED",
            category_name="Bedsheet",
            display_order=-5
        )

def test_category_update_omits_code():
    schema = CategoryUpdate(
        category_name="Bedsheet Updated",
        display_order=2
    )
    assert not hasattr(schema, "category_code")
    assert schema.category_name == "Bedsheet Updated"
