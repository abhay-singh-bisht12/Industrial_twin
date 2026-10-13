import pytest
from pydantic import ValidationError
from app.models.telemetry import TelemetryPayload

def test_valid_telemetry_payload():
    raw_data = {
        "motor_id": "motor-01",
        "timestamp": "2026-09-17T23:00:00+00:00",
        "temperature": 52.4,
        "vibration_rms": 1.45,
        "vibration_peak": 0.92,
        "rpm": 1475.0,
        "current_draw": 28.1,
        "voltage": 399.5,
        "load_percentage": 75.0,
        "operating_state": "NORMAL"
    }
    telemetry = TelemetryPayload(**raw_data)
    assert telemetry.motor_id == "motor-01"
    assert telemetry.temperature == 52.4
    assert telemetry.operating_state == "NORMAL"

def test_invalid_operating_state():
    raw_data = {
        "motor_id": "motor-01",
        "temperature": 50.0,
        "vibration_rms": 1.0,
        "vibration_peak": 0.8,
        "rpm": 1480.0,
        "current_draw": 25.0,
        "voltage": 400.0,
        "load_percentage": 50.0,
        "operating_state": "EXPLODED"  # Invalid state
    }
    with pytest.raises(ValidationError):
        TelemetryPayload(**raw_data)

def test_out_of_bounds_telemetry_values():
    raw_data = {
        "motor_id": "motor-01",
        "temperature": 500.0,  # Exceeds max 250.0 °C limit
        "vibration_rms": -5.0, # Negative vibration
        "vibration_peak": 0.8,
        "rpm": 1480.0,
        "current_draw": 25.0,
        "voltage": 400.0,
        "load_percentage": 50.0,
        "operating_state": "NORMAL"
    }
    with pytest.raises(ValidationError):
        TelemetryPayload(**raw_data)

def test_esp32_hardware_telemetry_payload_compatibility():
    esp32_json = {
        "motor_id": "esp32-motor-01",
        "temperature": 45.5,
        "vibration_rms": 1.25,
        "vibration_peak": 0.85,
        "rpm": 1480.0,
        "current_draw": 28.5,
        "voltage": 400.0,
        "load_percentage": 75.0,
        "operating_state": "NORMAL"
    }
    telemetry = TelemetryPayload(**esp32_json)
    assert telemetry.motor_id == "esp32-motor-01"
    assert telemetry.temperature == 45.5
    assert telemetry.vibration_rms == 1.25
    assert telemetry.operating_state == "NORMAL"
