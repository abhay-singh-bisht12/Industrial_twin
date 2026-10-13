import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["project"] == "IndustrialTwin"
    assert "timestamp" in data
    assert "database_connected" in data

@pytest.mark.asyncio
async def test_system_status_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/system-status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["version"] == "0.1.0"
    assert "services" in data
    assert "mongodb" in data["services"]
    assert "mqtt_broker" in data["services"]
