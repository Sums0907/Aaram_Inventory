import pytest
from pydantic import ValidationError
from src.domains.data_ingestion.schemas.integration import IntegrationCreate, IntegrationUpdate

def test_integration_create_valid():
    schema = IntegrationCreate(
        integration_code="SHOPDECK",
        integration_name="ShopDeck Aggregator",
        integration_type="MARKETPLACE"
    )
    assert schema.integration_code == "SHOPDECK"
    assert schema.integration_type == "MARKETPLACE"

def test_integration_update_omits_code():
    schema = IntegrationUpdate(
        integration_name="ShopDeck V2",
        integration_type="MARKETPLACE"
    )
    assert not hasattr(schema, "integration_code")
    assert schema.integration_name == "ShopDeck V2"
