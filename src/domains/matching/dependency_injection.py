from dependency_injector import containers, providers
from src.domains.matching.repositories.job import MatchJobRepository
from src.domains.matching.repositories.relationship import MatchRelationshipRepository
from src.domains.matching.repositories.exception import MatchExceptionRepository
from src.domains.matching.services.engine import MatchingEngineService

class MatchingContainer(containers.DeclarativeContainer):
    db = providers.Dependency()

    # Repositories
    job_repository = providers.Factory(
        MatchJobRepository,
        session=db.provided.scoped_session.call(),
    )
    relationship_repository = providers.Factory(
        MatchRelationshipRepository,
        session=db.provided.scoped_session.call(),
    )
    exception_repository = providers.Factory(
        MatchExceptionRepository,
        session=db.provided.scoped_session.call(),
    )

    # Services
    engine_service = providers.Factory(
        MatchingEngineService,
        session=db.provided.scoped_session.call(),
    )
