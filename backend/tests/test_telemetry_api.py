import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_recent_telemetry_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/telemetry/recent?motor_id=motor-01&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "motor_id" in data
    assert data["motor_id"] == "motor-01"
    assert "count" in data
    assert "data" in data
    assert isinstance(data["data"], list)

@pytest.mark.asyncio
async def test_get_motor_status_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/telemetry/status?motor_id=motor-01")
    assert response.status_code == 200
    data = response.json()
    assert data["motor_id"] == "motor-01"
    assert "operating_state" in data
    assert "temperature" in data
    assert "status_health" in data

@pytest.mark.asyncio
async def test_get_telemetry_stats_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/telemetry/stats?motor_id=motor-01&minutes=30")
    assert response.status_code == 200
    data = response.json()
    assert data["motor_id"] == "motor-01"
    assert data["time_window_minutes"] == 30
    assert "stats" in data

@pytest.mark.asyncio
async def test_control_motor_endpoint_all_states(async_client: AsyncClient, monkeypatch):
    from app.services.mqtt_service import mqtt_consumer_service
    from unittest.mock import AsyncMock

    mock_publish = AsyncMock(return_value=True)
    monkeypatch.setattr(mqtt_consumer_service, "publish_control_command", mock_publish)

    states = ["NORMAL", "OVERHEATING", "BEARING_WEAR", "ELECTRICAL_FAULT"]
    for state in states:
        payload = {
            "motor_id": "motor-01",
            "state": state,
            "load_percentage": 75.0
        }
        response = await async_client.post("/api/v1/telemetry/control", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert data["motor_id"] == "motor-01"
        assert data["command"]["state"] == state
        assert data["command"]["load_percentage"] == 75.0

    assert mock_publish.call_count == 4

@pytest.mark.asyncio
async def test_control_motor_endpoint_mqtt_unavailable(async_client: AsyncClient, monkeypatch):
    from app.services.mqtt_service import mqtt_consumer_service
    from unittest.mock import AsyncMock

    mock_publish = AsyncMock(return_value=False)
    monkeypatch.setattr(mqtt_consumer_service, "publish_control_command", mock_publish)

    payload = {
        "motor_id": "motor-01",
        "state": "OVERHEATING",
        "load_percentage": 90.0
    }
    response = await async_client.post("/api/v1/telemetry/control", json=payload)
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert "unavailable or disconnected" in data["detail"]

@pytest.mark.asyncio
async def test_control_motor_endpoint_invalid_load(async_client: AsyncClient):
    payload = {
        "motor_id": "motor-01",
        "state": "NORMAL",
        "load_percentage": 250.0  # Exceeds max 125.0
    }
    response = await async_client.post("/api/v1/telemetry/control", json=payload)
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_get_motor_list_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/telemetry/motors")
    assert response.status_code == 200
    data = response.json()
    assert "motors" in data
    assert "motor-01" in data["motors"]
