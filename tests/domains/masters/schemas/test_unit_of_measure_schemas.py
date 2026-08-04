import pytest
from pydantic import ValidationError
from src.domains.masters.schemas.unit_of_measure import UnitOfMeasureCreate, UnitOfMeasureUpdate

def test_unit_of_measure_create_valid():
    schema = UnitOfMeasureCreate(
        unit_code="PCS",
        unit_name="Pieces",
        short_name="pcs",
        description="Standard Pieces"
    )
    assert schema.unit_code == "PCS"
    assert schema.unit_name == "Pieces"

def test_unit_of_measure_create_invalid_blank_code():
    with pytest.raises(ValidationError):
        UnitOfMeasureCreate(
            unit_code="",
            unit_name="Pieces",
            short_name="pcs"
        )

def test_unit_of_measure_update_omits_code():
    schema = UnitOfMeasureUpdate(
        unit_name="Pieces Updated",
        short_name="pcs2"
    )
    assert not hasattr(schema, "unit_code")
    assert schema.unit_name == "Pieces Updated"
