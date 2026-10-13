from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class HealthPenaltyBreakdown(BaseModel):
    thermal: float = Field(..., description="Thermal penalty deduction")
    vibration: float = Field(..., description="Vibration penalty deduction")
    electrical: float = Field(..., description="Electrical penalty deduction")
    rpm_slip: float = Field(..., description="RPM slip penalty deduction")
    ml_anomaly: float = Field(..., description="ML anomaly penalty deduction")

class MachineHealthResponse(BaseModel):
    motor_id: str = Field(..., json_schema_extra={"example": "motor-01"})
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operating_state: str = Field(..., json_schema_extra={"example": "NORMAL"})
    composite_health_score: float = Field(..., ge=0.0, le=100.0, json_schema_extra={"example": 94.5})
    sensor_health_score: float = Field(..., ge=0.0, le=100.0, json_schema_extra={"example": 96.0})
    ml_anomaly_score: float = Field(..., ge=0.0, le=1.0, json_schema_extra={"example": 0.12})
    health_tier: str = Field(..., json_schema_extra={"example": "HEALTHY"})
    is_anomaly: bool = Field(..., json_schema_extra={"example": False})
    degradation_reasons: List[str] = Field(default_factory=list)
    penalty_breakdown: HealthPenaltyBreakdown

class HealthHistoryItem(BaseModel):
    timestamp: datetime
    composite_health_score: float
    health_tier: str
    operating_state: str
    temperature: float
    vibration_rms: float
    current_draw: float

class HealthHistoryResponse(BaseModel):
    motor_id: str
    count: int
    history: List[HealthHistoryItem]

class AnomalyAlertItem(BaseModel):
    motor_id: str
    timestamp: datetime
    operating_state: str
    composite_health_score: float
    ml_anomaly_score: float
    reasons: List[str]
    severity: str  # "WARNING", "CRITICAL"

class AnomalyAlertsResponse(BaseModel):
    count: int
    alerts: List[AnomalyAlertItem]

class ModelMetadataResponse(BaseModel):
    model_name: str
    model_version: str
    trained_at: str
    random_seed: int
    feature_columns: List[str]
    evaluation_metrics: Dict[str, Any]
    status: str
