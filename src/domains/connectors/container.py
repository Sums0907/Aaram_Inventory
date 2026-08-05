from dependency_injector import containers, providers
from src.domains.connectors.services.storage import StorageManager
from src.domains.connectors.services.shopdeck import ShopDeckConnector
from src.domains.connectors.services.sync import SyncService
from src.domains.connectors.services.base import CredentialProvider
from typing import Dict

class DummyCredentialProvider(CredentialProvider):
    def get_credentials(self, marketplace_id: str) -> Dict[str, str]:
        return {"dummy": "token"}

class ConnectorsContainer(containers.DeclarativeContainer):
    
    # Dependencies from other containers
    db_session = providers.Dependency()
    import_job_service = providers.Dependency()
    
    # Providers
    credential_provider = providers.Singleton(DummyCredentialProvider)
    
    storage_manager = providers.Singleton(
        StorageManager,
        base_storage_dir="storage"
    )
    
    shopdeck_connector = providers.Singleton(
        ShopDeckConnector,
        credential_provider=credential_provider
    )
    
    shopdeck_sync_service = providers.Factory(
        SyncService,
        session=db_session,
        connector=shopdeck_connector,
        storage_manager=storage_manager,
        import_job_service=import_job_service
    )
