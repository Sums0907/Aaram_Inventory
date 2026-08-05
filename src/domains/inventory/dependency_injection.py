from dependency_injector import containers, providers
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.repositories.exception import InventoryExceptionRepository

from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.services.ledger_service import InventoryLedgerService
from src.domains.inventory.services.confidence_engine import ConfidenceEngine
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService

class InventoryContainer(containers.DeclarativeContainer):
    db = providers.Dependency()

    movement_repository = providers.Factory(
        InventoryMovementRepository,
        session=db.provided._session_factory.call(),
    )
    
    balance_repository = providers.Factory(
        InventoryBalanceRepository,
        session=db.provided._session_factory.call(),
    )
    
    exception_repository = providers.Factory(
        InventoryExceptionRepository,
        session=db.provided._session_factory.call(),
    )

    movement_service = providers.Factory(
        InventoryMovementService,
        repository=movement_repository,
    )
    
    ledger_service = providers.Factory(
        InventoryLedgerService,
        movement_repository=movement_repository,
    )
    
    confidence_engine = providers.Factory(
        ConfidenceEngine,
        exception_repository=exception_repository,
        movement_repository=movement_repository,
    )
    
    balance_calculator = providers.Factory(
        BalanceCalculatorService,
        balance_repository=balance_repository,
        movement_repository=movement_repository,
        confidence_engine=confidence_engine,
    )
