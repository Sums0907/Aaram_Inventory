from dependency_injector import containers, providers
from src.foundation.dependency_injection.container import CoreContainer
from src.domains.masters.dependency_injection import MastersContainer

class DomainsContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()

    masters = providers.Container(
        MastersContainer,
        core=core,
    )
