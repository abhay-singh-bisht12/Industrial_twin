from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, status

from app.core.config import settings
from app.core.database import get_database
from app.models.telemetry import TelemetryPayload
from app.models.ml import (
    MachineHealthResponse,
    HealthHistoryResponse,
    HealthHistoryItem,
    AnomalyAlertsResponse,
    AnomalyAlertItem,
    ModelMetadataResponse
)
from app.services.ml_service import ml_service

router = APIRouter(prefix="/ml", tags=["Machine Learning & Health Engine"])

@router.get(
    "/health",
    response_model=MachineHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current Machine Health Evaluation"
)
async def get_current_machine_health(
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
        # Fallback evaluation on default baseline telemetry
        default_telemetry = TelemetryPayload(
            motor_id=motor_id,
            timestamp=datetime.now(timezone.utc),
            temperature=45.0,
            vibration_rms=1.2,
            vibration_peak=0.8,
            rpm=1480.0,
            current_draw=28.5,
            voltage=400.0,
            load_percentage=75.0,
            operating_state="NORMAL"
        )
        health_eval = ml_service.evaluate_telemetry(default_telemetry)
        return MachineHealthResponse(
            motor_id=motor_id,
            timestamp=datetime.now(timezone.utc),
            operating_state="NORMAL",
            composite_health_score=health_eval["composite_health_score"],
            sensor_health_score=health_eval["sensor_health_score"],
            ml_anomaly_score=health_eval["ml_anomaly_score"],
            health_tier=health_eval["health_tier"],
            is_anomaly=health_eval["is_anomaly"],
            degradation_reasons=health_eval["degradation_reasons"],
            penalty_breakdown=health_eval["penalty_breakdown"]
        )
        
    ts = latest_doc.get("timestamp")
    if not isinstance(ts, datetime):
        ts = datetime.fromisoformat(str(ts))

    telemetry = TelemetryPayload(
        motor_id=latest_doc.get("motor_id", motor_id),
        timestamp=ts,
        temperature=latest_doc.get("temperature", 45.0),
        vibration_rms=latest_doc.get("vibration_rms", 1.2),
        vibration_peak=latest_doc.get("vibration_peak", 0.8),
        rpm=latest_doc.get("rpm", 1480.0),
        current_draw=latest_doc.get("current_draw", 28.5),
        voltage=latest_doc.get("voltage", 400.0),
        load_percentage=latest_doc.get("load_percentage", 75.0),
        operating_state=latest_doc.get("operating_state", "NORMAL")
    )
    
    health_eval = ml_service.evaluate_telemetry(telemetry)
    return MachineHealthResponse(
        motor_id=motor_id,
        timestamp=ts,
        operating_state=telemetry.operating_state,
        composite_health_score=health_eval["composite_health_score"],
        sensor_health_score=health_eval["sensor_health_score"],
        ml_anomaly_score=health_eval["ml_anomaly_score"],
        health_tier=health_eval["health_tier"],
        is_anomaly=health_eval["is_anomaly"],
        degradation_reasons=health_eval["degradation_reasons"],
        penalty_breakdown=health_eval["penalty_breakdown"]
    )

@router.get(
    "/health/history",
    response_model=HealthHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Machine Health Score History"
)
async def get_health_history(
    motor_id: str = Query(default="motor-01", description="Motor ID"),
    limit: int = Query(default=50, ge=1, le=500, description="Max entries")
):
    db = get_database()
    history = []
    
    if db is not None:
        try:
            collection = db[settings.MONGO_TELEMETRY_COLLECTION]
            cursor = collection.find({"motor_id": motor_id}).sort("timestamp", -1).limit(limit)
            async for doc in cursor:
                ts = doc.get("timestamp")
                if not isinstance(ts, datetime):
                    ts = datetime.fromisoformat(str(ts))
                history.append(HealthHistoryItem(
                    timestamp=ts,
                    composite_health_score=doc.get("composite_health_score", 100.0),
                    health_tier=doc.get("health_tier", "HEALTHY"),
                    operating_state=doc.get("operating_state", "NORMAL"),
                    temperature=doc.get("temperature", 0.0),
                    vibration_rms=doc.get("vibration_rms", 0.0),
                    current_draw=doc.get("current_draw", 0.0)
                ))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    return HealthHistoryResponse(
        motor_id=motor_id,
        count=len(history),
        history=history
    )

@router.get(
    "/anomalies",
    response_model=AnomalyAlertsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Logged Anomaly Alerts"
)
async def get_anomalies(
    motor_id: Optional[str] = Query(default=None, description="Optional Motor ID filter"),
    limit: int = Query(default=50, ge=1, le=200, description="Max alerts")
):
    db = get_database()
    alerts = []
    
    if db is not None:
        try:
            collection = db[settings.MONGO_ALERTS_COLLECTION]
            query = {"motor_id": motor_id} if motor_id else {}
            cursor = collection.find(query).sort("timestamp", -1).limit(limit)
            async for doc in cursor:
                ts = doc.get("timestamp")
                if not isinstance(ts, datetime):
                    ts = datetime.fromisoformat(str(ts))
                alerts.append(AnomalyAlertItem(
                    motor_id=doc.get("motor_id", "unknown"),
                    timestamp=ts,
                    operating_state=doc.get("operating_state", "UNKNOWN"),
                    composite_health_score=doc.get("composite_health_score", 0.0),
                    ml_anomaly_score=doc.get("ml_anomaly_score", 0.0),
                    reasons=doc.get("reasons", []),
                    severity=doc.get("severity", "WARNING")
                ))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Alerts query error: {str(e)}")

    return AnomalyAlertsResponse(
        count=len(alerts),
        alerts=alerts
    )

@router.get(
    "/model-info",
    response_model=ModelMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get ML Anomaly Model Metadata & Performance Metrics"
)
async def get_model_info():
    metadata = ml_service.get_metadata()
    return ModelMetadataResponse(
        model_name=metadata.get("model_name", "IndustrialTwin_IsolationForest"),
        model_version=metadata.get("model_version", "1.0.0"),
        trained_at=str(metadata.get("trained_at", "N/A")),
        random_seed=metadata.get("random_seed", 42),
        feature_columns=metadata.get("feature_columns", []),
        evaluation_metrics=metadata.get("evaluation_metrics", {}),
        status=metadata.get("status", "active")
    )
