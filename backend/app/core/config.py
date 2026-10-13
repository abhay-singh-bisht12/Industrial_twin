import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find root directory containing .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "IndustrialTwin"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # FastAPI
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    SECRET_KEY: str = "dev_secret_key_industrial_twin"
    
    # MQTT Settings
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_WS_PORT: int = 9001
    MQTT_CLIENT_ID: str = "industrial_twin_backend"
    MQTT_TELEMETRY_TOPIC: str = "industrial/motor/+/telemetry"
    MQTT_ALERT_TOPIC: str = "industrial/motor/+/alerts"
    MQTT_CONTROL_TOPIC: str = "industrial/motor/+/control"
    
    # MongoDB Settings
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "industrial_twin"
    MONGO_TELEMETRY_COLLECTION: str = "telemetry"
    MONGO_ALERTS_COLLECTION: str = "alerts"
    
    # ML Model Settings
    ML_MODEL_PATH: str = "ml/models/health_model.joblib"
    ML_ANOMALY_THRESHOLD: float = 0.65
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
