from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

class TelemetryPayload(BaseModel):
    """Raw sensor telemetry payload matching hardware (ESP32 / Simulator)."""
    motor_id: str = Field(..., description="Unique motor identifier", json_schema_extra={"example": "motor-01"})
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of telemetry reading")
    temperature: float = Field(..., ge=-50.0, le=250.0, description="Temperature in °C")
    vibration_rms: float = Field(..., ge=0.0, le=100.0, description="Vibration RMS velocity in mm/s")
    vibration_peak: float = Field(..., ge=0.0, le=50.0, description="Vibration Peak acceleration in g")
    rpm: float = Field(..., ge=0.0, le=10000.0, description="Rotational speed in RPM")
    current_draw: float = Field(..., ge=0.0, le=500.0, description="Current draw in Amperes")
    voltage: float = Field(..., ge=0.0, le=1000.0, description="Line voltage in Volts")
    load_percentage: float = Field(..., ge=0.0, le=200.0, description="Load percentage (0-200%)")
    operating_state: str = Field(..., description="Operating status (NORMAL, OVERHEATING, BEARING_WEAR, ELECTRICAL_FAULT)")

    @field_validator("operating_state")
    @classmethod
    def validate_operating_state(cls, v: str) -> str:
        valid_states = {"NORMAL", "OVERHEATING", "BEARING_WEAR", "ELECTRICAL_FAULT"}
        v_upper = v.upper()
        if v_upper not in valid_states:
            raise ValueError(f"Invalid operating state '{v}'. Must be one of {valid_states}")
        return v_upper

class TelemetryDocument(TelemetryPayload):
    """Stored MongoDB telemetry document with optional record ID."""
    id: Optional[str] = Field(default=None, alias="_id")

class TelemetryQueryResponse(BaseModel):
    motor_id: str
    count: int
    data: List[TelemetryPayload]

class MotorStatusSummary(BaseModel):
    motor_id: str
    last_updated: datetime
    operating_state: str
    temperature: float
    vibration_rms: float
    current_draw: float
    rpm: float
    status_health: str  # "HEALTHY", "WARNING", "CRITICAL"

class MotorControlRequest(BaseModel):
    motor_id: str = Field(..., json_schema_extra={"example": "motor-01"})
    state: Optional[str] = Field(default=None, description="Target state (NORMAL, OVERHEATING, BEARING_WEAR, ELECTRICAL_FAULT)")
    load_percentage: Optional[float] = Field(default=None, ge=0.0, le=125.0, description="Target mechanical load percentage")
