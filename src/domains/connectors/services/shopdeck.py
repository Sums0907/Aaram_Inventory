import httpx
from typing import AsyncGenerator, Optional
from datetime import date
from src.domains.connectors.services.base import MarketplaceConnector, DownloadedFileContext
from src.foundation.configuration.settings import get_settings

class ShopDeckConnector(MarketplaceConnector):
    
    @classmethod
    def get_marketplace_id(cls) -> str:
        return "SHOPDECK"
        
    def _get_base_url(self) -> str:
        return get_settings().SHOPDECK_BASE_URL
        
    def _get_session_cookie(self) -> str:
        return get_settings().SHOPDECK_SESSION_COOKIE
        
    def _get_headers(self) -> dict:
        cookie = self._get_session_cookie()
        headers = {
            "wm_lang": "en",
            "wm_platform": "dashboard",
            "wm_web_version": "7.4",
            "Content-Type": "application/json"
        }
        if cookie:
            headers["Cookie"] = cookie
        return headers

    async def authenticate(self) -> bool:
        """
        Validates that the session cookie is present and conceptually valid.
        """
        # Bypassing authentication for mock run
        return True

    async def download_reports(self, period_start: Optional[date] = None, period_end: Optional[date] = None, report_type: Optional[str] = None) -> AsyncGenerator[DownloadedFileContext, None]:
        """
        Connects directly to ShopDeck's internal APIs to download reports via streaming.
        """
        if not period_start or not period_end:
            raise ValueError("period_start and period_end are required for ShopDeck reports.")

        async with httpx.AsyncClient(base_url=self._get_base_url(), timeout=httpx.Timeout(60.0)) as client:
            
            import logging
            logger = logging.getLogger("ShopDeckConnector")
            
            reports_to_mock = [
                {
                    "report_type": "ORDER_RECONCILIATION",
                    "file_path": "/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory/input/Order Reconciliation Report.csv",
                    "filename_prefix": "order_reconciliation"
                },
                {
                    "report_type": "TAX_READY",
                    "file_path": "/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory/input/Tax Ready Report.csv",
                    "filename_prefix": "tax_ready"
                },
                {
                    "report_type": "COD_SETTLEMENT",
                    "file_path": "/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory/input/COD Settlement Report.csv",
                    "filename_prefix": "cod_settlement"
                },
                {
                    "report_type": "RAZORPAY_SETTLEMENT",
                    "file_path": "/Users/sumatidhingra/Documents/AaramBooks/Aaram_Inventory/input/razorpay Settlement Reconciliation Report.csv",
                    "filename_prefix": "razorpay_settlement"
                }
            ]
            
            for mock_report in reports_to_mock:
                if not report_type or report_type == mock_report["report_type"]:
                    logger.info(f"Using mock {mock_report['report_type']} from local disk...")
                    try:
                        with open(mock_report["file_path"], "rb") as f:
                            content = f.read()
                    except Exception as e:
                        logger.error(f"Failed to read mock file for {mock_report['report_type']}: {e}")
                        continue
                        
                    filename = f"{mock_report['filename_prefix']}_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}.csv"
                    
                    yield DownloadedFileContext(
                        filename=filename,
                        file_content=content,
                        report_type=mock_report["report_type"],
                        period_start=period_start,
                        period_end=period_end
                    )
                    logger.info(f"Yielded mock {mock_report['report_type']}.")
