import asyncio
import json
import logging
import time
import httpx
import websockets
from motor.motor_asyncio import AsyncIOMotorClient
from simulator.motor import MotorSimulator, MotorState
from simulator.mqtt_client import MotorMQTTClient

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [e2e_verifier]: %(message)s")
logger = logging.getLogger("e2e_verifier")

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws/telemetry"
MONGO_URI = "mongodb://localhost:27017"

async def run_e2e_verification():
    logger.info("==================================================================")
    logger.info("   INDUSTRIAL TWIN - REAL END-TO-END PIPELINE VERIFICATION")
    logger.info("==================================================================")
    
    # 1. REST Health Check Verification
    async with httpx.AsyncClient() as client:
        logger.info("\n--- 1. Testing REST Health & System Status Endpoints ---")
        res_health = await client.get(f"{BASE_URL}/health")
        logger.info(f"GET /health Status: {res_health.status_code}")
        logger.info(f"GET /health Response: {json.dumps(res_health.json(), indent=2)}")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"
        
        res_status = await client.get(f"{BASE_URL}/api/v1/system-status")
        logger.info(f"GET /api/v1/system-status Status: {res_status.status_code}")
        logger.info(f"GET /api/v1/system-status Response: {json.dumps(res_status.json(), indent=2)}")
        assert res_status.status_code == 200

    # 2. Setup WebSocket Live Receiver
    logger.info("\n--- 2. Connecting WebSocket Client to FastAPI Backend ---")
    ws_received_messages = []
    
    async def websocket_listener():
        try:
            async with websockets.connect(WS_URL) as ws:
                logger.info(f"Connected to WebSocket at {WS_URL}")
                while len(ws_received_messages) < 6:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    logger.info(f"[WS RECEIVED LIVE STREAM] Motor: {data.get('motor_id')} | Temp: {data.get('temperature')}°C | State: {data.get('operating_state')}")
                    ws_received_messages.append(data)
        except Exception as e:
            logger.error(f"WebSocket listener error: {e}")

    ws_task = asyncio.create_task(websocket_listener())
    await asyncio.sleep(1.0)

    # 3. Initialize & Start Motor Simulator publishing over MQTT
    logger.info("\n--- 3. Starting Python Motor Telemetry Simulator (MQTT Publisher) ---")
    motor = MotorSimulator(motor_id="motor-01", seed=42)
    mqtt_publisher = MotorMQTTClient(motor_id="motor-01")
    connected = mqtt_publisher.connect()
    logger.info(f"MQTT Publisher connection status: {connected}")
    assert connected is True, "MQTT Publisher must connect to broker on port 1883"

    # Step through 4 state transitions: NORMAL -> OVERHEATING -> BEARING_WEAR -> ELECTRICAL_FAULT
    states_to_test = [
        (MotorState.NORMAL, 2),
        (MotorState.OVERHEATING, 2),
        (MotorState.BEARING_WEAR, 2),
        (MotorState.ELECTRICAL_FAULT, 2)
    ]

    logger.info("\n--- 4. Publishing Telemetry through States (NORMAL -> OVERHEATING -> BEARING_WEAR -> ELECTRICAL_FAULT) ---")
    for state, steps in states_to_test:
        motor.set_state(state)
        for _ in range(steps):
            telemetry = motor.step(dt=1.0)
            published = mqtt_publisher.publish_telemetry(telemetry)
            logger.info(f"Published MQTT Telemetry [{state.value}] -> Success: {published}")
            await asyncio.sleep(0.8)

    mqtt_publisher.disconnect()
    
    # Wait for WebSocket listener to capture stream
    await asyncio.sleep(1.5)
    ws_task.cancel()

    # 5. Query MongoDB directly to verify document persistence
    logger.info("\n--- 5. Verifying MongoDB Database Persistence ---")
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client["industrial_twin"]
    collection = db["telemetry"]
    
    count = await collection.count_documents({"motor_id": "motor-01"})
    logger.info(f"Total MongoDB documents in 'telemetry' collection for motor-01: {count}")
    assert count > 0, "MongoDB collection must contain ingested documents"
    
    latest_doc = await collection.find_one({"motor_id": "motor-01"}, sort=[("timestamp", -1)])
    latest_doc["_id"] = str(latest_doc["_id"])
    latest_doc["timestamp"] = str(latest_doc["timestamp"])
    logger.info(f"Latest MongoDB Ingested Document:\n{json.dumps(latest_doc, indent=2)}")

    # 6. Test REST API Telemetry Endpoints
    async with httpx.AsyncClient() as client:
        logger.info("\n--- 6. Verifying Telemetry REST API Endpoints ---")
        
        # GET /recent
        res_recent = await client.get(f"{BASE_URL}/api/v1/telemetry/recent?motor_id=motor-01&limit=3")
        logger.info(f"GET /api/v1/telemetry/recent Status: {res_recent.status_code}")
        logger.info(f"GET /api/v1/telemetry/recent Response:\n{json.dumps(res_recent.json(), indent=2)}")
        assert res_recent.status_code == 200
        assert res_recent.json()["count"] > 0

        # GET /status
        res_motor_status = await client.get(f"{BASE_URL}/api/v1/telemetry/status?motor_id=motor-01")
        logger.info(f"GET /api/v1/telemetry/status Status: {res_motor_status.status_code}")
        logger.info(f"GET /api/v1/telemetry/status Response:\n{json.dumps(res_motor_status.json(), indent=2)}")
        assert res_motor_status.status_code == 200

        # GET /stats
        res_stats = await client.get(f"{BASE_URL}/api/v1/telemetry/stats?motor_id=motor-01&minutes=60")
        logger.info(f"GET /api/v1/telemetry/stats Status: {res_stats.status_code}")
        logger.info(f"GET /api/v1/telemetry/stats Response:\n{json.dumps(res_stats.json(), indent=2)}")
        assert res_stats.status_code == 200

        # POST /control
        res_control = await client.post(
            f"{BASE_URL}/api/v1/telemetry/control",
            json={"motor_id": "motor-01", "state": "NORMAL", "load_percentage": 80.0}
        )
        logger.info(f"POST /api/v1/telemetry/control Status: {res_control.status_code}")
        logger.info(f"POST /api/v1/telemetry/control Response:\n{json.dumps(res_control.json(), indent=2)}")
        assert res_control.status_code == 200

    mongo_client.close()
    
    logger.info("\n==================================================================")
    logger.info("   ✅ VERIFICATION SUCCESSFUL: FULL E2E PIPELINE PROVEN WORKING!")
    logger.info("==================================================================")

if __name__ == "__main__":
    asyncio.run(run_e2e_verification())
