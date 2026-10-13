from fastapi import APIRouter, status
from app.core.config import settings
from app.core.database import db_wrapper
from app.models.health import HealthCheckResponse, SystemStatusResponse

router = APIRouter(tags=["Health & Status"])

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Check"
)
async def health_check():
    db_connected = False
    if db_wrapper.client is not None:
        try:
            # Ping database
            await db_wrapper.client.admin.command('ping')
            db_connected = True
        except Exception:
            db_connected = False
            
    return HealthCheckResponse(
        status="healthy" if db_connected or settings.ENVIRONMENT == "development" else "degraded",
        project=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        database_connected=db_connected
    )

@router.get(
    "/system-status",
    response_model=SystemStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed System & Subservice Status"
)
async def system_status():
    db_status = "disconnected"
    if db_wrapper.client is not None:
        try:
            await db_wrapper.client.admin.command('ping')
            db_status = "connected"
        except Exception:
            db_status = "error"

    return SystemStatusResponse(
        status="running",
        version="0.1.0",
        services={
            "mongodb": db_status,
            "mqtt_broker": "ready",
            "ml_engine": "ready"
        }
    )
