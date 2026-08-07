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
from src.domains.masters.repositories.product import ProductRepository
from src.domains.masters.services.product import ProductService
from src.domains.masters.repositories.sku import SKURepository
from src.domains.masters.services.sku import SKUService
from src.domains.masters.repositories.supplier import SupplierRepository
from src.domains.masters.services.supplier import SupplierService
from src.domains.masters.services.inventory_item import InventoryItemService
from src.domains.masters.services.hierarchy import InventoryHierarchyService

class MastersContainer(containers.DeclarativeContainer):
    db = providers.Dependency()

    # Repositories
    company_repository = providers.Factory(
        CompanyRepository,
        session=db.provided._session_factory.call(),
    )
    unit_of_measure_repository = providers.Factory(
        UnitOfMeasureRepository,
        session=db.provided._session_factory.call(),
    )
    warehouse_repository = providers.Factory(
        WarehouseRepository,
        session=db.provided._session_factory.call(),
    )
    category_repository = providers.Factory(
        CategoryRepository,
        session=db.provided._session_factory.call(),
    )
    product_attribute_repository = providers.Factory(
        ProductAttributeRepository,
        session=db.provided._session_factory.call(),
    )
    product_repository = providers.Factory(
        ProductRepository,
        session=db.provided._session_factory.call(),
    )
    sku_repository = providers.Factory(
        SKURepository,
        session=db.provided._session_factory.call(),
    )
    supplier_repository = providers.Factory(
        SupplierRepository,
        session=db.provided._session_factory.call(),
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
    product_service = providers.Factory(
        ProductService,
        repository=product_repository,
        category_repo=category_repository,
    )
    sku_service = providers.Factory(
        SKUService,
        repository=sku_repository,
        product_repo=product_repository,
    )
    supplier_service = providers.Factory(
        SupplierService,
        repository=supplier_repository,
    )
    inventory_item_service = providers.Factory(
        InventoryItemService,
        session=db.provided._session_factory.call(),
    )
    inventory_hierarchy_service = providers.Factory(
        InventoryHierarchyService,
        session=db.provided._session_factory.call(),
    )
