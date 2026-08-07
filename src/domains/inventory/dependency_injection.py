from dependency_injector import containers, providers
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.repositories.exception import InventoryExceptionRepository
from src.domains.inventory.repositories.goods_receipt import GoodsReceiptRepository
from src.domains.inventory.repositories.purchase_return import PurchaseReturnRepository

from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.services.ledger_service import InventoryLedgerService
from src.domains.inventory.services.confidence_engine import ConfidenceEngine
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService
from src.domains.inventory.services.goods_receipt import GoodsReceiptService
from src.domains.inventory.services.purchase_return import PurchaseReturnService

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
    
    goods_receipt_repository = providers.Factory(
        GoodsReceiptRepository,
        session=db.provided._session_factory.call(),
    )

    purchase_return_repository = providers.Factory(
        PurchaseReturnRepository,
        session=db.provided._session_factory.call(),
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
        exception_repository=exception_repository,
        confidence_engine=confidence_engine,
    )

    movement_service = providers.Factory(
        InventoryMovementService,
        repository=movement_repository,
        balance_calculator=balance_calculator,
    )
    
    ledger_service = providers.Factory(
        InventoryLedgerService,
        movement_repository=movement_repository,
    )

    goods_receipt_service = providers.Factory(
        GoodsReceiptService,
        repository=goods_receipt_repository,
        movement_service=movement_service,
    )

    purchase_return_service = providers.Factory(
        PurchaseReturnService,
        repository=purchase_return_repository,
        movement_service=movement_service,
    )
