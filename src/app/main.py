from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.foundation.configuration import get_settings
from src.foundation.api.health import router as health_router
from src.foundation.exceptions.handlers import register_exception_handlers
from src.foundation.api.middleware import RequestContextMiddleware
from src.foundation.logging import setup_logging
from src.foundation.dependency_injection import CoreContainer
from src.app.container import DomainsContainer
from src.domains.masters.api import router as masters_router
from src.app.api.setup import router as setup_router

def create_app() -> FastAPI:
    settings = get_settings()
    
    # Set up JSON structured logging
    setup_logging(settings.LOG_LEVEL)
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG
    )
    
    # Initialize Dependency Injection Container
    core_container = CoreContainer()
    core_container.config.from_pydantic(settings)
    
    domains_container = DomainsContainer(core=core_container)
    
    app.core_container = core_container
    app.domains_container = domains_container
    
    # CORS Middleware (Frozen Strategy: explicit origins, never "*")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom Middleware
    app.add_middleware(RequestContextMiddleware)
    
    # Exception Handlers
    register_exception_handlers(app)
    
    # System Routers (Mounted at root for Kubernetes)
    app.include_router(health_router)
    
    # API Versioning Scaffolding
    api_v1_router = APIRouter(prefix="/api/v1")
    
    # System Setup (Installation & Configuration)
    api_v1_router.include_router(setup_router, prefix="/setup")
    
    # Domains
    api_v1_router.include_router(masters_router, prefix="/masters")
    
    app.include_router(api_v1_router)
    
    return app

app = create_app()
