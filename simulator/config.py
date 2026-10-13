from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class SimulatorSettings(BaseSettings):
    MOTOR_ID: str = "motor-01"
    MOTOR_RATED_POWER_KW: float = 15.0  # 15 kW industrial induction motor
    MOTOR_RATED_SPEED_RPM: float = 1480.0
    MOTOR_NOMINAL_VOLTAGE: float = 400.0  # 400V 3-phase
    
    # MQTT Config
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_CLIENT_ID: str = "industrial_twin_simulator"
    MQTT_TELEMETRY_TOPIC_TEMPLATE: str = "industrial/motor/{motor_id}/telemetry"
    MQTT_CONTROL_TOPIC_TEMPLATE: str = "industrial/motor/{motor_id}/control"
    
    # Simulation Timing
    PUBLISH_INTERVAL_SEC: float = 1.0
    
    # Baseline Parameters (NORMAL State)
    BASE_TEMPERATURE_C: float = 45.0
    BASE_VIBRATION_RMS_MM_S: float = 1.2
    BASE_VIBRATION_PEAK_G: float = 0.8
    BASE_CURRENT_DRAW_A: float = 28.5
    BASE_VOLTAGE_V: float = 400.0
    BASE_LOAD_PCT: float = 75.0
    
    # Fault Parameter Escalations
    OVERHEATING_TEMP_C: float = 95.0
    BEARING_WEAR_VIBRATION_RMS: float = 6.8
    BEARING_WEAR_VIBRATION_PEAK: float = 4.5
    ELECTRICAL_FAULT_CURRENT_A: float = 52.0
    ELECTRICAL_FAULT_VOLTAGE_V: float = 365.0
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

sim_settings = SimulatorSettings()
