from dependency_injector import containers, providers
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.services.movement import InventoryMovementService

class InventoryContainer(containers.DeclarativeContainer):
    db = providers.Dependency()

    movement_repository = providers.Factory(
        InventoryMovementRepository,
        session=db.provided._session_factory.call(),
    )

    movement_service = providers.Factory(
        InventoryMovementService,
        repository=movement_repository,
    )
