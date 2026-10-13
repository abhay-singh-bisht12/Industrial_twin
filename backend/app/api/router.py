from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.ws import router as ws_router
from app.api.v1.ml import router as ml_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(telemetry_router)
api_router.include_router(ws_router)
api_router.include_router(ml_router)
