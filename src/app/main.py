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
from src.domains.data_ingestion.api import router as data_ingestion_router
from src.domains.matching.api import router as matching_router
from src.domains.connectors.api.shopdeck_router import router as shopdeck_router
from src.domains.accounting.api.export_router import router as accounting_export_router
from src.app.api.dashboard import router as dashboard_router
from src.app.api.setup import router as setup_router
from src.api.v1.read_api_router import read_api_router
from src.api.v1.master_data_router import master_data_router

def create_app() -> FastAPI:
    settings = get_settings()
    
    # Set up JSON structured logging
    setup_logging(settings.LOG_LEVEL)
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG
    )
    
    print(f"\nAARAMBOOKS {'CERTIFICATION' if settings.DATABASE_ENV.lower() == 'test' else 'DATABASE'}")
    print("-" * 25)
    print(f"Environment: {settings.DATABASE_ENV.upper()}")
    print(f"Database: {settings.DATABASE_URL.split('///')[-1] if 'sqlite' in settings.DATABASE_URL else settings.DATABASE_URL}\n")
    
    # Initialize Dependency Injection Container
    domains_container = DomainsContainer()
    domains_container.core.config.from_dict(settings.model_dump())
    app.core_container = domains_container.core
    app.domains_container = domains_container
    
    domains_container.core().wire(packages=["src.app", "src.foundation"])
    domains_container.masters().wire(packages=["src.domains.masters"])
    domains_container.operations().wire(packages=["src.domains.operations"])
    domains_container.data_ingestion().wire(packages=["src.domains.data_ingestion", "src.api.v1"])
    domains_container.matching().wire(packages=["src.domains.matching"])
    domains_container.inventory().wire(packages=["src.domains.inventory", "src.api.v1"])
    domains_container.accounting().wire(packages=["src.domains.accounting", "src.api.v1"])
    domains_container.connectors().wire(packages=["src.domains.connectors"])
    domains_container.wire(modules=[
        "src.api.v1.read_api_router", 
        "src.api.v1.master_data_router",
        "src.domains.matching.api.router", 
        "src.app.api.dashboard", 
        "src.domains.accounting.api.export_router",
        "src.domains.accounting.api.journal_router",
        "src.domains.inventory.api.router",
        "src.domains.inventory.api.movement_router",
        "src.domains.inventory.api.dashboard_router",
        "src.domains.inventory.api.item_workspace",
        "src.domains.inventory.api.goods_receipt",
        "src.domains.inventory.api.purchase_return",
        "src.domains.inventory.api.job_work",
        "src.domains.inventory.api.exception_router",
        "src.domains.inventory.api.packer_webhook_router",
        "src.domains.connectors.api.shopdeck_router",
        "src.domains.operations.api.lifecycle_router",
        "src.domains.masters.api.supplier",
        "src.domains.accounting.job_worker.api.rates",
        "src.domains.accounting.job_worker.api.expenses",
        "src.domains.accounting.job_worker.api.payments",
        "src.domains.accounting.job_worker.api.payables",
    ])
    
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
    api_v1_router.include_router(data_ingestion_router, prefix="/data-ingestion")
    api_v1_router.include_router(matching_router, prefix="/matching")
    from src.domains.inventory.api.router import router as inv_router
    from src.domains.inventory.api.movement_router import router as inv_mov_router
    from src.domains.inventory.api.dashboard_router import router as inv_dash_router
    from src.domains.inventory.api.item_workspace import router as item_workspace_router
    from src.domains.inventory.api.goods_receipt import router as grn_router
    from src.domains.inventory.api.purchase_return import router as pr_router
    from src.domains.inventory.api.job_work import router as job_work_router
    from src.domains.inventory.api.exception_router import router as exception_router
    from src.domains.operations.api.lifecycle_router import router as lifecycle_router
    from src.domains.inventory.api.packer_webhook_router import router as packer_router
    api_v1_router.include_router(inv_router)
    api_v1_router.include_router(inv_mov_router)
    api_v1_router.include_router(inv_dash_router)
    api_v1_router.include_router(item_workspace_router)
    api_v1_router.include_router(grn_router, prefix="/inventory")
    api_v1_router.include_router(pr_router, prefix="/inventory")
    api_v1_router.include_router(job_work_router)
    api_v1_router.include_router(exception_router)
    api_v1_router.include_router(packer_router)
    api_v1_router.include_router(shopdeck_router, prefix="/shopdeck")
    api_v1_router.include_router(lifecycle_router, prefix="/operations")
    api_v1_router.include_router(accounting_export_router, prefix="/accounting/export")
    from src.domains.accounting.api.journal_router import router as jrn_router
    api_v1_router.include_router(jrn_router, prefix="/accounting")
    # Job Worker Accounting sub-domain
    from src.domains.accounting.job_worker.api.rates import router as jw_rates_router
    from src.domains.accounting.job_worker.api.expenses import router as jw_expenses_router
    from src.domains.accounting.job_worker.api.payments import router as jw_payments_router
    from src.domains.accounting.job_worker.api.payables import router as jw_payables_router
    api_v1_router.include_router(jw_rates_router)
    api_v1_router.include_router(jw_expenses_router)
    api_v1_router.include_router(jw_payments_router)
    api_v1_router.include_router(jw_payables_router)
    api_v1_router.include_router(dashboard_router, prefix="/dashboard")
    api_v1_router.include_router(read_api_router)
    api_v1_router.include_router(master_data_router)
    
    app.include_router(api_v1_router)
    
    import os
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    # Serve Single Page Application (SPA) if dist exists
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
    if os.path.isdir(frontend_dir):
        # Mount assets directory
        assets_dir = os.path.join(frontend_dir, "assets")
        if os.path.isdir(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
            
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            file_path = os.path.join(frontend_dir, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(frontend_dir, "index.html"))
    
    return app

app = create_app()
