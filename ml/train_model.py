import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [ml_trainer]: %(message)s")
logger = logging.getLogger("ml_trainer")

FEATURE_COLUMNS = [
    "temperature",
    "vibration_rms",
    "vibration_peak",
    "rpm",
    "current_draw",
    "voltage",
    "load_percentage",
    "power_factor_approx",
    "vibration_crest_factor"
]

MODEL_VERSION = "1.0.0"

def preprocess_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and derive features from raw telemetry dataframe."""
    df_feat = df.copy()
    
    # Derived Feature 1: Power Factor approximation
    df_feat["power_factor_approx"] = df_feat["current_draw"] / np.maximum(df_feat["voltage"], 100.0)
    
    # Derived Feature 2: Vibration Crest Factor (Peak / RMS)
    df_feat["vibration_crest_factor"] = df_feat["vibration_peak"] / np.maximum(df_feat["vibration_rms"], 0.1)
    
    return df_feat[FEATURE_COLUMNS]

def train_isolation_forest(
    dataset_path: Path,
    model_output_path: Path,
    metadata_output_path: Path,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Trains Isolation Forest model for anomaly detection.
    Precludes data leakage by fitting scaler on normal training data.
    """
    logger.info(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    # Feature extraction
    X = preprocess_features(df)
    y_binary = (df["operating_state"] != "NORMAL").astype(int)  # 0: Normal, 1: Anomaly
    
    # Split train/test (Train on NORMAL samples to learn baseline normal behavior)
    normal_mask = (df["operating_state"] == "NORMAL")
    X_normal = X[normal_mask]
    
    # 80/20 train/test split on normal samples
    split_idx = int(len(X_normal) * 0.8)
    X_train_normal = X_normal.iloc[:split_idx]
    
    # Test set includes remaining normal samples + ALL fault samples
    X_test_normal = X_normal.iloc[split_idx:]
    X_test_faults = X[~normal_mask]
    
    X_test = pd.concat([X_test_normal, X_test_faults])
    y_test = np.concatenate([
        np.zeros(len(X_test_normal)),
        np.ones(len(X_test_faults))
    ])
    
    # Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_normal)
    X_test_scaled = scaler.transform(X_test)
    
    # Isolation Forest Model Initialization & Training
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=seed,
        n_jobs=-1
    )
    model.fit(X_train_scaled)
    
    # Predictions: IsolationForest outputs +1 for inliers (normal), -1 for outliers (anomalies)
    raw_preds = model.predict(X_test_scaled)
    y_pred = np.where(raw_preds == -1, 1, 0)
    
    # Decision function raw scores (more negative = more anomalous)
    raw_scores = model.decision_function(X_test_scaled)
    # Convert decision score to 0.0 - 1.0 anomaly score (0: Normal, 1: Highly Anomalous)
    anomaly_scores = np.clip(0.5 - raw_scores, 0.0, 1.0)
    
    # Evaluation Metrics
    report = classification_report(y_test, y_pred, output_dict=True)
    auc = float(roc_auc_score(y_test, anomaly_scores))
    cm = confusion_matrix(y_test, y_pred).tolist()
    class_1_key = 1 if 1 in report else ("1" if "1" in report else 1.0)
    
    metrics = {
        "precision_anomaly": float(report[class_1_key]["precision"]) if class_1_key in report else 0.0,
        "recall_anomaly": float(report[class_1_key]["recall"]) if class_1_key in report else 0.0,
        "f1_anomaly": float(report[class_1_key]["f1-score"]) if class_1_key in report else 0.0,
        "accuracy": float(report["accuracy"]),
        "roc_auc": auc,
        "confusion_matrix": cm
    }
    
    logger.info(f"Model Evaluation Metrics:\n"
                f"  Accuracy: {metrics['accuracy']:.4f}\n"
                f"  Precision (Anomaly): {metrics['precision_anomaly']:.4f}\n"
                f"  Recall (Anomaly): {metrics['recall_anomaly']:.4f}\n"
                f"  F1-Score (Anomaly): {metrics['f1_anomaly']:.4f}\n"
                f"  ROC-AUC: {metrics['roc_auc']:.4f}")
    
    # Package artifact containing both scaler and model
    artifact = {
        "scaler": scaler,
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "version": MODEL_VERSION
    }
    
    model_output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_output_path)
    logger.info(f"Saved trained model artifact to {model_output_path}")
    
    # Save Metadata JSON
    metadata = {
        "model_name": "IndustrialTwin_IsolationForest",
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "training_samples_normal": len(X_train_normal),
        "test_samples_total": len(X_test),
        "feature_columns": FEATURE_COLUMNS,
        "evaluation_metrics": metrics,
        "note": "Trained on synthetic simulation dataset. Anomaly scores indicate deviation from baseline normal physics."
    }
    
    metadata_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_output_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved model metadata to {metadata_output_path}")
    
    return metadata

def main():
    parser = argparse.ArgumentParser(description="Train ML Anomaly Detection Model")
    parser.add_argument("--dataset", type=str, default="ml/data/motor_telemetry_dataset.csv", help="Input dataset path")
    parser.add_argument("--model-out", type=str, default="ml/models/health_model.joblib", help="Output model joblib path")
    parser.add_argument("--metadata-out", type=str, default="ml/models/model_metadata.json", help="Output metadata json path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()
    train_isolation_forest(
        dataset_path=Path(args.dataset),
        model_output_path=Path(args.model_out),
        metadata_output_path=Path(args.metadata_out),
        seed=args.seed
    )

if __name__ == "__main__":
    main()
