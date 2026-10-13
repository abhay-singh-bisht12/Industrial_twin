import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import paho.mqtt.client as mqtt

from app.core.config import settings
from app.core.database import get_database
from app.models.telemetry import TelemetryPayload
from app.services.websocket_manager import ws_manager

logger = logging.getLogger("industrial_twin.mqtt_consumer")

class MQTTConsumerService:
    """
    FastAPI MQTT Background Consumer Service.
    Subscribes to telemetry topics, validates payloads, stores to MongoDB,
    and broadcasts to WebSocket clients.
    """
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.is_connected = True
            logger.info(f"MQTT Consumer connected to broker {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
            client.subscribe(settings.MQTT_TELEMETRY_TOPIC)
            logger.info(f"Subscribed to telemetry topic: {settings.MQTT_TELEMETRY_TOPIC}")
        else:
            self.is_connected = False
            logger.error(f"MQTT Consumer failed to connect, return code: {rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self.is_connected = False
        if rc != 0:
            logger.warning(f"MQTT Consumer disconnected unexpectedly (rc={rc}). Broker will retry...")
        else:
            logger.info("MQTT Consumer disconnected gracefully.")

    def _on_message(self, client, userdata, msg):
        """Callback executed on receiving MQTT message."""
        try:
            payload_str = msg.payload.decode("utf-8")
            raw_data = json.loads(payload_str)
            
            # Parse & validate schema using Pydantic
            telemetry = TelemetryPayload(**raw_data)
            
            # Schedule async database insertion and WebSocket broadcast on event loop
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self._process_and_store_telemetry(telemetry),
                    self.loop
                )
            else:
                logger.warning("Event loop not running; telemetry message skipped DB save.")
                
        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON payload on topic {msg.topic}: {e}")
        except Exception as e:
            logger.error(f"Validation error or processing failure on topic {msg.topic}: {e}")

    async def _process_and_store_telemetry(self, telemetry: TelemetryPayload):
        """Persist telemetry to MongoDB, apply ML scoring, and broadcast via WebSocket."""
        try:
            # 1. Run ML & Health Engine Evaluation
            from app.services.ml_service import ml_service
            health_eval = ml_service.evaluate_telemetry(telemetry)

            # 2. Prepare Augmented Telemetry Record
            telemetry_dict = telemetry.model_dump()
            if isinstance(telemetry_dict.get("timestamp"), str):
                telemetry_dict["timestamp"] = datetime.fromisoformat(telemetry_dict["timestamp"])

            # Attach health & anomaly metrics
            telemetry_dict["composite_health_score"] = health_eval["composite_health_score"]
            telemetry_dict["sensor_health_score"] = health_eval["sensor_health_score"]
            telemetry_dict["ml_anomaly_score"] = health_eval["ml_anomaly_score"]
            telemetry_dict["health_tier"] = health_eval["health_tier"]
            telemetry_dict["is_anomaly"] = health_eval["is_anomaly"]
            telemetry_dict["degradation_reasons"] = health_eval["degradation_reasons"]

            db = get_database()
            if db is not None:
                # 3. Store Telemetry Record in MongoDB
                col_telemetry = db[settings.MONGO_TELEMETRY_COLLECTION]
                await col_telemetry.insert_one(telemetry_dict)
                logger.debug(f"Telemetry for {telemetry.motor_id} (Health: {health_eval['composite_health_score']}) saved to DB")

                # 4. Store Anomaly Alert Document in MongoDB if abnormal
                if health_eval["is_anomaly"] or health_eval["health_tier"] == "CRITICAL":
                    alert_doc = {
                        "motor_id": telemetry.motor_id,
                        "timestamp": telemetry_dict["timestamp"],
                        "operating_state": telemetry.operating_state,
                        "composite_health_score": health_eval["composite_health_score"],
                        "ml_anomaly_score": health_eval["ml_anomaly_score"],
                        "reasons": health_eval["degradation_reasons"],
                        "severity": "CRITICAL" if health_eval["health_tier"] == "CRITICAL" else "WARNING"
                    }
                    col_alerts = db[settings.MONGO_ALERTS_COLLECTION]
                    await col_alerts.insert_one(alert_doc)
                    logger.info(f"Anomaly Alert logged for motor '{telemetry.motor_id}': {health_eval['degradation_reasons']}")
            else:
                logger.debug("MongoDB unavailable; telemetry received but not persisted")

            # 5. WebSocket Realtime Broadcast (Augmented)
            ws_payload = telemetry.model_dump(mode="json")
            ws_payload.update(health_eval)
            await ws_manager.broadcast(ws_payload)

        except Exception as e:
            logger.error(f"Error persisting/broadcasting telemetry: {e}")

    def start(self):
        """Start MQTT Consumer client loop."""
        if self.client is not None:
            logger.warning("MQTT Consumer service already running.")
            return

        try:
            self.loop = asyncio.get_running_loop()
            self.client = mqtt.Client(
                client_id=f"{settings.MQTT_CLIENT_ID}_backend",
                protocol=mqtt.MQTTv311
            )
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            logger.info(f"Connecting MQTT Consumer to {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}...")
            self.client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to start MQTT Consumer service: {e}")
            self.client = None

    def stop(self):
        """Stop MQTT Consumer client loop."""
        if self.client:
            logger.info("Stopping MQTT Consumer background loop...")
            self.client.loop_stop()
            self.client.disconnect()
            self.client = None
            self.is_connected = False
            logger.info("MQTT Consumer service stopped.")

    async def publish_control_command(self, motor_id: str, command: Dict[str, Any]) -> bool:
        """Publish control command to simulator control topic."""
        # Wait up to 2.0 seconds if client is currently connecting
        if self.client and not self.is_connected:
            start_wait = asyncio.get_running_loop().time()
            while not self.is_connected and (asyncio.get_running_loop().time() - start_wait) < 2.0:
                await asyncio.sleep(0.05)

        if not self.client or not self.is_connected:
            logger.warning("Cannot publish control command: MQTT Consumer not connected to broker.")
            return False
            
        topic = settings.MQTT_CONTROL_TOPIC.replace("+", motor_id)
        try:
            payload_str = json.dumps(command)
            res = self.client.publish(topic, payload_str, qos=1)
            logger.info(f"Published control command to {topic}: {command}")
            return res.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Failed to publish control command to {topic}: {e}")
            return False

mqtt_consumer_service = MQTTConsumerService()
