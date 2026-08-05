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

@pytest.mark.asyncio
async def test_authenticate_unauthorized(connector):
    mock_response = MagicMock()
    mock_response.status_code = 401

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=MockAsyncContextManager(mock_client)):
        assert await connector.authenticate() is False

@pytest.mark.asyncio
async def test_authenticate_missing_cookie(connector, monkeypatch):
    monkeypatch.setenv("SHOPDECK_SESSION_COOKIE", "")
    assert await connector.authenticate() is False

@pytest.mark.asyncio
async def test_download_reports_success(connector):
    period_start = date(2026, 4, 1)
    period_end = date(2026, 4, 30)

    mock_stream_response = AsyncMock()
    mock_stream_response.status_code = 200
    mock_stream_response.aread.return_value = b"header1,header2\nval1,val2"
    
    mock_client = MagicMock()
    # stream returns an async context manager that yields the mock_stream_response
    mock_client.stream.return_value = MockAsyncContextManager(mock_stream_response)

    with patch("httpx.AsyncClient", return_value=MockAsyncContextManager(mock_client)):
        results = []
        async for report in connector.download_reports(period_start, period_end):
            results.append(report)
            
        assert len(results) == 2
        
        assert results[0].report_type == "ORDER_RECONCILIATION"
        assert results[0].filename == "order_reconciliation_20260401_20260430.csv"
        assert results[0].file_content == b"header1,header2\nval1,val2"

        assert results[1].report_type == "TAX_READY"
        assert results[1].filename == "tax_ready_04-2026.csv"
        assert results[1].file_content == b"header1,header2\nval1,val2"

@pytest.mark.asyncio
async def test_download_reports_unauthorized(connector):
    period_start = date(2026, 4, 1)
    period_end = date(2026, 4, 30)

    mock_stream_response = AsyncMock()
    mock_stream_response.status_code = 401
    
    mock_client = MagicMock()
    mock_client.stream.return_value = MockAsyncContextManager(mock_stream_response)

    with patch("httpx.AsyncClient", return_value=MockAsyncContextManager(mock_client)):
        with pytest.raises(PermissionError, match="ShopDeck session expired."):
            async for report in connector.download_reports(period_start, period_end):
                pass

