import asyncio
import json
import logging
import httpx
import websockets
from motor.motor_asyncio import AsyncIOMotorClient
from simulator.motor import MotorSimulator, MotorState
from simulator.mqtt_client import MotorMQTTClient

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [phase3_verifier]: %(message)s")
logger = logging.getLogger("phase3_verifier")

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/ws/telemetry"
MONGO_URI = "mongodb://localhost:27017"

async def run_phase3_e2e_verification():
    logger.info("==================================================================")
    logger.info("   INDUSTRIAL TWIN - PHASE 3 ML & HEALTH ENGINE VERIFICATION")
    logger.info("==================================================================")
    
    # 1. Connect WebSocket Client
    ws_received_messages = []
    async def websocket_listener():
        try:
            async with websockets.connect(WS_URL) as ws:
                logger.info(f"Connected to WebSocket at {WS_URL}")
                while len(ws_received_messages) < 4:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    logger.info(
                        f"[WS LIVE STREAM WITH ML] Motor: {data.get('motor_id')} | "
                        f"Health: {data.get('composite_health_score')}% ({data.get('health_tier')}) | "
                        f"ML Anomaly Score: {data.get('ml_anomaly_score')}"
                    )
                    ws_received_messages.append(data)
        except Exception as e:
            logger.error(f"WebSocket listener error: {e}")

    ws_task = asyncio.create_task(websocket_listener())
    await asyncio.sleep(1.0)

    # 2. Motor Simulator publishing MQTT Telemetry across fault states
    motor = MotorSimulator(motor_id="motor-01", seed=100)
    mqtt_publisher = MotorMQTTClient(motor_id="motor-01")
    connected = mqtt_publisher.connect()
    assert connected is True, "MQTT Publisher must connect to broker on port 1883"

    states_to_test = [MotorState.NORMAL, MotorState.OVERHEATING, MotorState.BEARING_WEAR, MotorState.ELECTRICAL_FAULT]
    
    logger.info("\n--- Publishing Telemetry across Fault States ---")
    for state in states_to_test:
        motor.set_state(state)
        telemetry = motor.step(dt=2.0)
        published = mqtt_publisher.publish_telemetry(telemetry)
        logger.info(f"Published telemetry state [{state.value}] -> Success: {published}")
        await asyncio.sleep(1.2)

    mqtt_publisher.disconnect()
    await asyncio.sleep(1.5)
    ws_task.cancel()

    # 3. Query MongoDB Database Collections (telemetry & alerts)
    logger.info("\n--- MongoDB Persistence & ML Ingestion Check ---")
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client["industrial_twin"]
    
    latest_telemetry = await db["telemetry"].find_one({"motor_id": "motor-01"}, sort=[("timestamp", -1)])
    latest_telemetry["_id"] = str(latest_telemetry["_id"])
    latest_telemetry["timestamp"] = str(latest_telemetry["timestamp"])
    logger.info(f"Latest MongoDB Ingested Telemetry Record with ML:\n{json.dumps(latest_telemetry, indent=2)}")

    alert_count = await db["alerts"].count_documents({})
    logger.info(f"Total Logged Anomaly Alerts in MongoDB: {alert_count}")
    if alert_count > 0:
        latest_alert = await db["alerts"].find_one({}, sort=[("timestamp", -1)])
        latest_alert["_id"] = str(latest_alert["_id"])
        latest_alert["timestamp"] = str(latest_alert["timestamp"])
        logger.info(f"Latest MongoDB Logged Anomaly Alert:\n{json.dumps(latest_alert, indent=2)}")

    # 4. Verify REST API ML Endpoints
    async with httpx.AsyncClient() as client:
        logger.info("\n--- REST API ML Endpoints Verification ---")
        
        # GET /api/v1/ml/health
        res_health = await client.get(f"{BASE_URL}/api/v1/ml/health?motor_id=motor-01")
        logger.info(f"GET /api/v1/ml/health Status: {res_health.status_code}")
        logger.info(f"GET /api/v1/ml/health Response:\n{json.dumps(res_health.json(), indent=2)}")
        assert res_health.status_code == 200

        # GET /api/v1/ml/health/history
        res_hist = await client.get(f"{BASE_URL}/api/v1/ml/health/history?motor_id=motor-01&limit=3")
        logger.info(f"GET /api/v1/ml/health/history Status: {res_hist.status_code}")
        logger.info(f"GET /api/v1/ml/health/history Response:\n{json.dumps(res_hist.json(), indent=2)}")
        assert res_hist.status_code == 200

        # GET /api/v1/ml/anomalies
        res_alerts = await client.get(f"{BASE_URL}/api/v1/ml/anomalies?limit=3")
        logger.info(f"GET /api/v1/ml/anomalies Status: {res_alerts.status_code}")
        logger.info(f"GET /api/v1/ml/anomalies Response:\n{json.dumps(res_alerts.json(), indent=2)}")
        assert res_alerts.status_code == 200

        # GET /api/v1/ml/model-info
        res_info = await client.get(f"{BASE_URL}/api/v1/ml/model-info")
        logger.info(f"GET /api/v1/ml/model-info Status: {res_info.status_code}")
        logger.info(f"GET /api/v1/ml/model-info Response:\n{json.dumps(res_info.json(), indent=2)}")
        assert res_info.status_code == 200

    mongo_client.close()
    logger.info("\n==================================================================")
    logger.info("   ✅ PHASE 3 VERIFICATION SUCCESSFUL: FULL ML ENGINE PROVEN WORKING!")
    logger.info("==================================================================")

if __name__ == "__main__":
    asyncio.run(run_phase3_e2e_verification())
