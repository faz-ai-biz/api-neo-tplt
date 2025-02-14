from fastapi import APIRouter

from .endpoints import files
from .endpoints.hello import router as hello_router
from .endpoints.metrics import router as metrics_router
from .endpoints.users import router as users_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(files.router)
api_router.include_router(hello_router)
api_router.include_router(metrics_router)
api_router.include_router(users_router)
