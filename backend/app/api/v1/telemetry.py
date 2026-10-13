from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from app.core.config import settings
from app.core.database import get_database
from app.models.telemetry import TelemetryPayload, TelemetryQueryResponse, MotorStatusSummary, MotorControlRequest
from app.services.mqtt_service import mqtt_consumer_service

router = APIRouter(prefix="/telemetry", tags=["Telemetry Operations"])

@router.get(
    "/recent",
    response_model=TelemetryQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Recent Telemetry Readings"
)
async def get_recent_telemetry(
    motor_id: str = Query(default="motor-01", description="Motor ID"),
    limit: int = Query(default=50, ge=1, le=500, description="Max readings to return")
):
    db = get_database()
    readings = []
    
    if db is not None:
        try:
            collection = db[settings.MONGO_TELEMETRY_COLLECTION]
            cursor = collection.find({"motor_id": motor_id}).sort("timestamp", -1).limit(limit)
            async for doc in cursor:
                doc["_id"] = str(doc.get("_id"))
                if isinstance(doc.get("timestamp"), datetime):
                    doc["timestamp"] = doc["timestamp"].isoformat()
                readings.append(TelemetryPayload(**doc))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    return TelemetryQueryResponse(
        motor_id=motor_id,
        count=len(readings),
        data=readings
    )

@router.get(
    "/status",
    response_model=MotorStatusSummary,
    status_code=status.HTTP_200_OK,
    summary="Get Current Motor Status Summary"
)
async def get_motor_status(
    motor_id: str = Query(default="motor-01", description="Motor ID")
):
    db = get_database()
    latest_doc = None
    
    if db is not None:
        try:
            collection = db[settings.MONGO_TELEMETRY_COLLECTION]
            latest_doc = await collection.find_one({"motor_id": motor_id}, sort=[("timestamp", -1)])
        except Exception:
            latest_doc = None
            
    if not latest_doc:
        # Fallback default when no database records present yet
        return MotorStatusSummary(
            motor_id=motor_id,
            last_updated=datetime.now(timezone.utc),
            operating_state="NORMAL",
            temperature=45.0,
            vibration_rms=1.2,
            current_draw=28.5,
            rpm=1480.0,
            status_health="HEALTHY"
        )
        
    state = latest_doc.get("operating_state", "NORMAL").upper()
    health_str = "HEALTHY"
    if state == "OVERHEATING" or state == "BEARING_WEAR":
        health_str = "WARNING"
    elif state == "ELECTRICAL_FAULT":
        health_str = "CRITICAL"

    ts = latest_doc.get("timestamp")
    if not isinstance(ts, datetime):
        ts = datetime.fromisoformat(str(ts))

    return MotorStatusSummary(
        motor_id=motor_id,
        last_updated=ts,
        operating_state=state,
        temperature=latest_doc.get("temperature", 0.0),
        vibration_rms=latest_doc.get("vibration_rms", 0.0),
        current_draw=latest_doc.get("current_draw", 0.0),
        rpm=latest_doc.get("rpm", 0.0),
        status_health=health_str
    )

@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Get Aggregate Metric Statistics"
)
async def get_telemetry_stats(
    motor_id: str = Query(default="motor-01", description="Motor ID"),
    minutes: int = Query(default=60, ge=1, le=1440, description="Time window in minutes")
):
    db = get_database()
    if db is None:
        return {
            "motor_id": motor_id,
            "time_window_minutes": minutes,
            "sample_count": 0,
            "stats": {}
        }
        
    since_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    pipeline = [
        {"$match": {"motor_id": motor_id, "timestamp": {"$gte": since_time}}},
        {
            "$group": {
                "_id": "$motor_id",
                "sample_count": {"$sum": 1},
                "avg_temp": {"$avg": "$temperature"},
                "max_temp": {"$max": "$temperature"},
                "avg_vib_rms": {"$avg": "$vibration_rms"},
                "max_vib_rms": {"$max": "$vibration_rms"},
                "avg_current": {"$avg": "$current_draw"},
                "max_current": {"$max": "$current_draw"},
                "avg_rpm": {"$avg": "$rpm"}
            }
        }
    ]
    
    try:
        collection = db[settings.MONGO_TELEMETRY_COLLECTION]
        results = await collection.aggregate(pipeline).to_list(length=1)
        if results:
            res = results[0]
            return {
                "motor_id": motor_id,
                "time_window_minutes": minutes,
                "sample_count": res["sample_count"],
                "stats": {
                    "temperature": {"avg": round(res["avg_temp"], 2), "max": round(res["max_temp"], 2)},
                    "vibration_rms": {"avg": round(res["avg_vib_rms"], 2), "max": round(res["max_vib_rms"], 2)},
                    "current_draw": {"avg": round(res["avg_current"], 2), "max": round(res["max_current"], 2)},
                    "rpm": {"avg": round(res["avg_rpm"], 1)}
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats calculation failed: {str(e)}")

    return {
        "motor_id": motor_id,
        "time_window_minutes": minutes,
        "sample_count": 0,
        "stats": {}
    }

@router.post(
    "/control",
    status_code=status.HTTP_200_OK,
    summary="Send Control Command to Motor Simulator"
)
async def control_motor(request: MotorControlRequest):
    command = {}
    if request.state:
        command["state"] = request.state
    if request.load_percentage is not None:
        command["load_percentage"] = request.load_percentage
        
    if not command:
        raise HTTPException(status_code=400, detail="Must provide at least one control action ('state' or 'load_percentage')")
        
    sent = await mqtt_consumer_service.publish_control_command(request.motor_id, command)
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT broker is unavailable or disconnected. Control command could not be delivered."
        )

    return {
        "status": "published",
        "motor_id": request.motor_id,
        "command": command
    }

@router.get(
    "/motors",
    status_code=status.HTTP_200_OK,
    summary="Get List of Available Motors"
)
async def get_motor_list():
    db = get_database()
    motors = ["motor-01", "motor-02", "motor-03", "motor-04"]
    if db is not None:
        try:
            collection = db[settings.MONGO_TELEMETRY_COLLECTION]
            distinct_motors = await collection.distinct("motor_id")
            if distinct_motors:
                motors = list(set(motors + distinct_motors))
                motors.sort()
        except Exception:
            pass
    return {"motors": motors}
