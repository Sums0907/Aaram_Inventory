from fastapi import APIRouter
from .shopdeck_import import router as shopdeck_import_router
from .import_job import router as import_job_router
from .integration import router as integration_router
from .commit import router as commit_router

# Use prefix="" here because main.py already prefixes this with /api/v1/data-ingestion
router = APIRouter()
router.include_router(shopdeck_import_router)
router.include_router(import_job_router)
router.include_router(integration_router)
router.include_router(commit_router)
