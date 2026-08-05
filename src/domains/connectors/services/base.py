import abc
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import date

@dataclass
class DownloadedFileContext:
    filename: str
    file_content: bytes
    report_type: str
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None

class CredentialProvider(abc.ABC):
    """
    Abstracts the retrieval of marketplace credentials.
    """
    @abc.abstractmethod
    def get_credentials(self, marketplace_id: str) -> Dict[str, str]:
        pass

class MarketplaceConnector(abc.ABC):
    """
    Abstract base class for any marketplace connector (ShopDeck, Shopify, Amazon, etc).
    """
    
    def __init__(self, credential_provider: CredentialProvider):
        self.credential_provider = credential_provider
        self.marketplace_id = self.get_marketplace_id()

    @classmethod
    @abc.abstractmethod
    def get_marketplace_id(cls) -> str:
        """Returns the unique identifier for this marketplace (e.g., 'SHOPDECK')"""
        pass
        
    @abc.abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticates with the marketplace. Must handle session persistence if needed.
        Returns True if successful, False otherwise.
        """
        pass

    @abc.abstractmethod
    async def download_reports(self, period_start: Optional[date] = None, period_end: Optional[date] = None) -> AsyncGenerator[DownloadedFileContext, None]:
        """
        Downloads all relevant reports for the given time period.
        Yields DownloadedFileContext objects containing raw bytes and metadata.
        """
        pass
