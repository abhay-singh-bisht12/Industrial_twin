import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd

from app.core.config import settings
from app.models.telemetry import TelemetryPayload
from ml.health_scoring import calculate_machine_health

logger = logging.getLogger("industrial_twin.ml_service")

class MLService:
    """
    ML Inference & Health Scoring Engine Service.
    Loads trained Isolation Forest model artifacts and evaluates incoming telemetry streams.
    """
    def __init__(self, model_path: Optional[Path] = None):
        if model_path:
            self.model_path = Path(model_path)
        else:
            # Resolve relative to project root directory
            backend_dir = Path(__file__).resolve().parent.parent.parent
            root_dir = backend_dir.parent
            candidate_path = Path(settings.ML_MODEL_PATH)
            if not candidate_path.is_absolute():
                self.model_path = root_dir / candidate_path
            else:
                self.model_path = candidate_path
                
        self.metadata_path = self.model_path.parent / "model_metadata.json"
        
        self.scaler = None
        self.model = None
        self.feature_columns = []
        self.metadata: Dict[str, Any] = {}
        self.is_loaded = False
        
        self.load_model()

    def load_model(self) -> bool:
        """Load model artifact and metadata safely."""
        try:
            if not self.model_path.exists():
                logger.warning(f"ML model file not found at {self.model_path}. ML service will use rule-based fallback mode.")
                self.is_loaded = False
                return False
                
            artifact = joblib.load(self.model_path)
            self.scaler = artifact.get("scaler")
            self.model = artifact.get("model")
            self.feature_columns = artifact.get("feature_columns", [])
            
            if self.metadata_path.exists():
                with open(self.metadata_path, "r") as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {"version": "1.0.0", "status": "loaded_without_metadata_file"}
                
            self.is_loaded = True
            logger.info(f"Successfully loaded ML model artifact (Version: {self.metadata.get('model_version', '1.0.0')})")
            return True
        except Exception as e:
            logger.error(f"Error loading ML model file {self.model_path}: {e}")
            self.is_loaded = False
            return False

    def evaluate_telemetry(self, telemetry: TelemetryPayload) -> Dict[str, Any]:
        """
        Evaluate telemetry reading using ML Isolation Forest model + Physics Health Engine.
        """
        ml_anomaly_score = 0.0
        
        if self.is_loaded and self.model is not None and self.scaler is not None:
            try:
                # 1. Feature Engineering
                raw_dict = telemetry.model_dump()
                current_draw = raw_dict["current_draw"]
                voltage = raw_dict["voltage"]
                vib_rms = raw_dict["vibration_rms"]
                vib_peak = raw_dict["vibration_peak"]
                
                pf_approx = current_draw / max(voltage, 100.0)
                vib_crest = vib_peak / max(vib_rms, 0.1)
                
                feat_df = pd.DataFrame([{
                    "temperature": raw_dict["temperature"],
                    "vibration_rms": vib_rms,
                    "vibration_peak": vib_peak,
                    "rpm": raw_dict["rpm"],
                    "current_draw": current_draw,
                    "voltage": voltage,
                    "load_percentage": raw_dict["load_percentage"],
                    "power_factor_approx": pf_approx,
                    "vibration_crest_factor": vib_crest
                }])[self.feature_columns]
                
                # 2. Scaling & Prediction
                feat_scaled = self.scaler.transform(feat_df)
                raw_decision = self.model.decision_function(feat_scaled)[0]
                
                # Convert decision score to normalized anomaly score in [0.0, 1.0]
                ml_anomaly_score = float(np.clip(0.5 - raw_decision, 0.0, 1.0))
                
            except Exception as e:
                logger.error(f"ML evaluation error on telemetry: {e}. Fallback scoring applied.")
                ml_anomaly_score = 0.0
                
        # 3. Calculate Composite Machine Health
        health_eval = calculate_machine_health(
            temperature=telemetry.temperature,
            vibration_rms=telemetry.vibration_rms,
            vibration_peak=telemetry.vibration_peak,
            current_draw=telemetry.current_draw,
            voltage=telemetry.voltage,
            rpm=telemetry.rpm,
            load_percentage=telemetry.load_percentage,
            ml_anomaly_score=ml_anomaly_score,
            operating_state=telemetry.operating_state
        )
        
        return health_eval

    def get_metadata(self) -> Dict[str, Any]:
        """Return model metadata for API endpoint."""
        if self.is_loaded:
            return {
                "model_name": self.metadata.get("model_name", "IndustrialTwin_IsolationForest"),
                "model_version": self.metadata.get("model_version", "1.0.0"),
                "trained_at": self.metadata.get("trained_at", "N/A"),
                "random_seed": self.metadata.get("random_seed", 42),
                "feature_columns": self.feature_columns,
                "evaluation_metrics": self.metadata.get("evaluation_metrics", {}),
                "status": "active"
            }
        else:
            return {
                "model_name": "Rule_Based_Fallback_Scorer",
                "model_version": "0.0.0",
                "status": "model_file_missing_using_rule_fallback"
            }

ml_service = MLService()
