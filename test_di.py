from dependency_injector import containers, providers

class CoreContainer(containers.DeclarativeContainer):
    db = providers.Singleton(dict)

class OperationsContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()
    sales_order_service = providers.Factory(dict, name="sales_service", session=core.db.provided.session)

class DataIngestionContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()
    operations = providers.DependenciesContainer()
    commit_service = providers.Factory(
        dict,
        sales=operations.sales_order_service
    )

class DomainsContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()
    operations = providers.Container(OperationsContainer, core=core)
    data_ingestion = providers.Container(
        DataIngestionContainer,
        core=core,
        operations=operations
    )

core_container = CoreContainer()
d = DomainsContainer(core=core_container)
print(d.data_ingestion().commit_service())
