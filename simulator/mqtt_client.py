import json
import logging
import time
from typing import Callable, Optional, Dict, Any
import paho.mqtt.client as mqtt
from simulator.config import sim_settings

logger = logging.getLogger("industrial_twin.mqtt_publisher")

class MotorMQTTClient:
    """
    Robust MQTT client wrapper for publishing telemetry and listening to control commands.
    Supports Paho MQTT v2 API with connection handling and auto-reconnect.
    """
    def __init__(
        self,
        broker_host: Optional[str] = None,
        broker_port: Optional[int] = None,
        client_id: Optional[str] = None,
        motor_id: Optional[str] = None
    ):
        self.broker_host = broker_host or sim_settings.MQTT_BROKER_HOST
        self.broker_port = broker_port or sim_settings.MQTT_BROKER_PORT
        self.client_id = client_id or sim_settings.MQTT_CLIENT_ID
        self.motor_id = motor_id or sim_settings.MOTOR_ID
        
        self.telemetry_topic = sim_settings.MQTT_TELEMETRY_TOPIC_TEMPLATE.format(motor_id=self.motor_id)
        self.control_topic = sim_settings.MQTT_CONTROL_TOPIC_TEMPLATE.format(motor_id=self.motor_id)
        
        self.is_connected = False
        self._on_control_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        
        # Paho MQTT Client setup
        self.client = mqtt.Client(
            client_id=f"{self.client_id}_{self.motor_id}",
            protocol=mqtt.MQTTv311
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.is_connected = True
            logger.info(f"Connected to MQTT Broker at {self.broker_host}:{self.broker_port}")
            # Subscribe to control topic
            client.subscribe(self.control_topic)
            logger.info(f"Subscribed to control topic: {self.control_topic}")
        else:
            self.is_connected = False
            logger.error(f"Failed to connect to MQTT Broker, return code: {rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT Broker (rc={rc}). Attempting auto-reconnect...")
        else:
            logger.info("Disconnected from MQTT Broker gracefully.")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            logger.info(f"Received control command on {msg.topic}: {payload}")
            if self._on_control_callback:
                self._on_control_callback(payload)
        except Exception as e:
            logger.error(f"Error processing control message on {msg.topic}: {e}")

    def set_control_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register callback for handling control messages."""
        self._on_control_callback = callback

    def connect(self) -> bool:
        """Connect to broker and start background loop."""
        try:
            logger.info(f"Connecting to MQTT Broker at {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            # Wait up to 3 seconds for connection confirmation
            timeout = time.time() + 3.0
            while not self.is_connected and time.time() < timeout:
                time.sleep(0.1)
            return self.is_connected
        except Exception as e:
            logger.error(f"Could not connect to MQTT broker at {self.broker_host}:{self.broker_port}: {e}")
            return False

    def publish_telemetry(self, telemetry: Dict[str, Any]) -> bool:
        """Publish telemetry JSON payload to MQTT topic."""
        if not self.is_connected:
            logger.warning(f"MQTT client not connected. Message for {self.telemetry_topic} dropped or queued.")
            
        try:
            payload_str = json.dumps(telemetry)
            result = self.client.publish(self.telemetry_topic, payload_str, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published telemetry to {self.telemetry_topic}: {telemetry['operating_state']}")
                return True
            else:
                logger.error(f"Failed to publish telemetry to {self.telemetry_topic}, result code: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing telemetry payload: {e}")
            return False

    def disconnect(self):
        """Disconnect client and stop background loop."""
        logger.info("Stopping MQTT client loop and disconnecting...")
        self.client.loop_stop()
        self.client.disconnect()
        self.is_connected = False
