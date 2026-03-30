from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.images import router as images_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.operations import router as operations_router
from app.api.v1.pipelines import router as pipelines_router
from app.api.v1.websocket import router as websocket_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(images_router)
api_router.include_router(pipelines_router)
api_router.include_router(jobs_router)
api_router.include_router(operations_router)
api_router.include_router(websocket_router)
