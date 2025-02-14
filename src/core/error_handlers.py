from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from datetime import datetime
import uuid

from src.core.exceptions import (
    CustomAppException,
    InvalidTokenError,
    FileNotFoundError,
)

def create_error_response(code: str, message: str, status_code: int) -> dict:
    """Create standardized error response format"""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": None,
            "requestId": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        }
    }

async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle generic HTTP exceptions"""
    error_code = "AUTH001" if exc.status_code == 401 else f"HTTP{exc.status_code}"
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            code=error_code,
            message=str(exc.detail),
            status_code=exc.status_code
        )
    )

def setup_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with the FastAPI application."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(FileNotFoundError, file_not_found_handler)
