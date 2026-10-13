import pytest
from pathlib import Path
from httpx import AsyncClient
from app.models.telemetry import TelemetryPayload
from app.services.ml_service import MLService, ml_service

def test_ml_service_missing_model_fallback(tmp_path: Path):
    non_existent_model = tmp_path / "missing_model.joblib"
    service = MLService(model_path=non_existent_model)
    assert service.is_loaded is False
    
    # Test fallback evaluation on normal telemetry
    payload = TelemetryPayload(
        motor_id="motor-01",
        temperature=45.0,
        vibration_rms=1.2,
        vibration_peak=0.8,
        rpm=1480.0,
        current_draw=28.0,
        voltage=400.0,
        load_percentage=75.0,
        operating_state="NORMAL"
    )
    res = service.evaluate_telemetry(payload)
    assert res["composite_health_score"] >= 90.0
    assert service.get_metadata()["status"] == "model_file_missing_using_rule_fallback"

def test_ml_service_loaded_evaluation():
    payload = TelemetryPayload(
        motor_id="motor-01",
        temperature=50.0,
        vibration_rms=1.3,
        vibration_peak=0.85,
        rpm=1478.0,
        current_draw=28.5,
        voltage=399.0,
        load_percentage=75.0,
        operating_state="NORMAL"
    )
    res = ml_service.evaluate_telemetry(payload)
    assert "composite_health_score" in res
    assert "ml_anomaly_score" in res
    assert "health_tier" in res

@pytest.mark.asyncio
async def test_ml_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/ml/health?motor_id=motor-01")
    assert response.status_code == 200
    data = response.json()
    assert data["motor_id"] == "motor-01"
    assert "composite_health_score" in data
    assert "health_tier" in data
    assert "penalty_breakdown" in data

@pytest.mark.asyncio
async def test_ml_health_history_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/ml/health/history?motor_id=motor-01&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["motor_id"] == "motor-01"
    assert "history" in data

@pytest.mark.asyncio
async def test_ml_anomalies_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/ml/anomalies?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data

@pytest.mark.asyncio
async def test_ml_model_info_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/ml/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "model_version" in data
    assert "feature_columns" in data
