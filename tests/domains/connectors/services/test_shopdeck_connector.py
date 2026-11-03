import pytest
from datetime import date
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.domains.connectors.services.shopdeck import ShopDeckConnector
from src.domains.connectors.services.base import CredentialProvider
from src.foundation.configuration.settings import get_settings

class DummyCredentialProvider(CredentialProvider):
    def get_credentials(self, marketplace_id: str) -> dict:
        return {"session_cookie": "dummy_cookie"}

@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield

@pytest.fixture
def connector(monkeypatch):
    provider = DummyCredentialProvider()
    conn = ShopDeckConnector(provider)
    monkeypatch.setenv("SHOPDECK_BASE_URL", "https://mock.shopdeck.com")
    monkeypatch.setenv("SHOPDECK_SESSION_COOKIE", "test_cookie_123")
    return conn

# Helper to mock AsyncContextManager
class MockAsyncContextManager:
    def __init__(self, return_value):
        self.return_value = return_value
    async def __aenter__(self):
        return self.return_value
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.mark.asyncio
async def test_authenticate_success(connector):
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=MockAsyncContextManager(mock_client)):
        assert await connector.authenticate() is True

