from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.foundation.dependency_injection.container import CoreContainer

async def get_db_session(
    session: AsyncSession = Depends(Provide[CoreContainer.db.provided.session])
) -> AsyncSession:
    """
    FastAPI Dependency that yields an AsyncSession.
    Extracts the session from the CoreContainer's Database provider.
    """
    return session
