from fastapi import APIRouter
from src.foundation.configuration import get_settings

router = APIRouter(tags=["System"])
settings = get_settings()

@router.get("/health")
async def health_check():
    """Aggregate health check."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@router.get("/liveness")
async def liveness_probe():
    """Kubernetes liveness probe. Indicates if the container is running."""
    return {"status": "alive"}

@router.get("/readiness")
async def readiness_probe():
    """Kubernetes readiness probe. Indicates if the app is ready to accept traffic."""
    # In the future, this should check DB connectivity, Redis, etc.
    return {"status": "ready"}
