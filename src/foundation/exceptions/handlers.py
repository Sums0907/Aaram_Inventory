from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, PendingRollbackError
from .base import BusinessException
from src.foundation.logging import get_logger

logger = get_logger("foundation.exceptions")

def format_error_response(code: str, message: str, details: dict = None) -> dict:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
        logger.warning(f"Business Exception: {exc.code} - {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content=format_error_response(exc.code, exc.message, exc.details)
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content=format_error_response("VALIDATION_ERROR", "Request validation failed", {"errors": exc.errors()})
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=format_error_response("HTTP_ERROR", str(exc.detail))
        )

    @app.exception_handler(IntegrityError)
    async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.error(f"Database Integrity Error: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content=format_error_response("DATA_INTEGRITY_ERROR", "This operation could not be completed because it violates data integrity constraints. An item might already exist or depend on something else.")
        )

    @app.exception_handler(PendingRollbackError)
    async def sqlalchemy_rollback_error_handler(request: Request, exc: PendingRollbackError) -> JSONResponse:
        logger.error(f"Database Transaction Error: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content=format_error_response("TRANSACTION_ERROR", "A database transaction error occurred. Please try again.")
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_general_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error(f"Database Error: {str(exc)}")
        msg = str(exc)
        if "greenlet_spawn" in msg:
            return JSONResponse(
                status_code=400,
                content=format_error_response("DATABASE_ERROR", "A database error occurred during an asynchronous operation. Please try again.")
            )
        return JSONResponse(
            status_code=500,
            content=format_error_response("DATABASE_ERROR", "An unexpected database error occurred.")
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        import traceback
        try:
            with open("/tmp/error_trace.log", "w") as f:
                traceback.print_exc(file=f)
        except Exception as log_exc:
            logger.error(f"Failed to write error trace to /tmp: {log_exc}")
        
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=format_error_response("INTERNAL_SERVER_ERROR", "An unexpected error occurred.")
        )
