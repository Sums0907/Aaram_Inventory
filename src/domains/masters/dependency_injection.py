from dependency_injector import containers, providers
from src.foundation.dependency_injection.container import CoreContainer
from src.domains.masters.repositories.company import CompanyRepository
from src.domains.masters.services.company import CompanyService
from src.domains.masters.repositories.unit_of_measure import UnitOfMeasureRepository
from src.domains.masters.services.unit_of_measure import UnitOfMeasureService
from src.domains.masters.repositories.warehouse import WarehouseRepository
from src.domains.masters.services.warehouse import WarehouseService
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.services.category import CategoryService
from src.domains.masters.repositories.product_attribute import ProductAttributeRepository
from src.domains.masters.services.product_attribute import ProductAttributeService
from src.domains.masters.repositories.inventory_item import InventoryItemRepository
from src.domains.masters.services.inventory_item import InventoryItemService
from src.domains.masters.repositories.sku import SKURepository
from src.domains.masters.services.sku import SKUService

class MastersContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()

    # Repositories
    company_repository = providers.Factory(
        CompanyRepository,
        session=core.db.provided.session,
    )
    unit_of_measure_repository = providers.Factory(
        UnitOfMeasureRepository,
        session=core.db.provided.session,
    )
    warehouse_repository = providers.Factory(
        WarehouseRepository,
        session=core.db.provided.session,
    )
    category_repository = providers.Factory(
        CategoryRepository,
        session=core.db.provided.session,
    )
    product_attribute_repository = providers.Factory(
        ProductAttributeRepository,
        session=core.db.provided.session,
    )
    inventory_item_repository = providers.Factory(
        InventoryItemRepository,
        session=core.db.provided.session,
    )
    sku_repository = providers.Factory(
        SKURepository,
        session=core.db.provided.session,
    )

    # Services
    company_service = providers.Factory(
        CompanyService,
        repository=company_repository,
    )
    unit_of_measure_service = providers.Factory(
        UnitOfMeasureService,
        repository=unit_of_measure_repository,
    )
    warehouse_service = providers.Factory(
        WarehouseService,
        repository=warehouse_repository,
    )
    category_service = providers.Factory(
        CategoryService,
        repository=category_repository,
    )
    product_attribute_service = providers.Factory(
        ProductAttributeService,
        repository=product_attribute_repository,
    )
    inventory_item_service = providers.Factory(
        InventoryItemService,
        repository=inventory_item_repository,
        category_repo=category_repository,
        uom_repo=unit_of_measure_repository,
    )
    sku_service = providers.Factory(
        SKUService,
        repository=sku_repository,
        item_repo=inventory_item_repository,
    )
