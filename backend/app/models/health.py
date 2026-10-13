from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class HealthCheckResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    project: str = Field(..., json_schema_extra={"example": "IndustrialTwin"})
    environment: str = Field(..., json_schema_extra={"example": "development"})
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    database_connected: bool = Field(..., json_schema_extra={"example": True})

class SystemStatusResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "running"})
    version: str = Field(..., json_schema_extra={"example": "0.1.0"})
    services: Dict[str, Any] = Field(
        ...,
        json_schema_extra={
            "example": {
                "mongodb": "connected",
                "mqtt_broker": "connected",
                "ml_engine": "loaded"
            }
        }
    )

