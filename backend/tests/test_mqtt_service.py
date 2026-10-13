import json
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.mqtt_service import MQTTConsumerService
from app.models.telemetry import TelemetryPayload

@pytest.mark.asyncio
async def test_mqtt_service_process_valid_payload():
    service = MQTTConsumerService()
    
    mock_payload = {
        "motor_id": "test-motor-01",
        "timestamp": "2026-09-17T23:00:00+00:00",
        "temperature": 48.5,
        "vibration_rms": 1.3,
        "vibration_peak": 0.85,
        "rpm": 1478.0,
        "current_draw": 28.0,
        "voltage": 401.0,
        "load_percentage": 75.0,
        "operating_state": "NORMAL"
    }
    
    telemetry = TelemetryPayload(**mock_payload)
    # Verify processing does not throw error
    await service._process_and_store_telemetry(telemetry)

def test_mqtt_service_on_message_handles_malformed_json():
    service = MQTTConsumerService()
    msg = MagicMock()
    msg.topic = "industrial/motor/motor-01/telemetry"
    msg.payload = b"NOT_VALID_JSON{{"
    
    # Executing on_message on malformed JSON should log error and not crash
    service._on_message(None, None, msg)

@pytest.mark.asyncio
async def test_publish_control_command_success():
    service = MQTTConsumerService()
    service.client = MagicMock()
    service.is_connected = True
    
    mock_res = MagicMock()
    mock_res.rc = 0
    service.client.publish.return_value = mock_res
    
    command = {"state": "ELECTRICAL_FAULT", "load_percentage": 75.0}
    success = await service.publish_control_command("motor-01", command)
    
    assert success is True
    service.client.publish.assert_called_once_with(
        "industrial/motor/motor-01/control",
        json.dumps(command),
        qos=1
    )

@pytest.mark.asyncio
async def test_publish_control_command_disconnected():
    service = MQTTConsumerService()
    service.client = None
    service.is_connected = False
    
    command = {"state": "NORMAL", "load_percentage": 50.0}
    success = await service.publish_control_command("motor-01", command)
    assert success is False
