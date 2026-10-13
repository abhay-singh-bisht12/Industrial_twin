import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add project root directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import connect_to_mongo, close_mongo_connection
from app.services.mqtt_service import mqtt_consumer_service
from app.api.router import api_router
from app.api.v1.health import router as root_health_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} backend service...")
    await connect_to_mongo()
    mqtt_consumer_service.start()
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME} backend service...")
    mqtt_consumer_service.stop()
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Industrial Equipment Health Monitoring & Digital Twin Platform Backend",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(root_health_router)  # /health at root level
app.include_router(api_router)           # /api/v1/...

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
