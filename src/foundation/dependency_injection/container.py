from dependency_injector import containers, providers
from src.foundation.configuration import get_settings
from src.foundation.database import Database

class CoreContainer(containers.DeclarativeContainer):
    """
    Core dependency injection container for the foundation layer.
    """
    # Configuration
    config = providers.Configuration()
    
    # Database
    db = providers.Singleton(
        Database,
        db_url=config.DATABASE_URL,
        debug=config.DEBUG,
        pool_size=config.DB_POOL_SIZE,
        max_overflow=config.DB_MAX_OVERFLOW,
    )
    
    # Providers can be added for JWT / Auth services here as well.
