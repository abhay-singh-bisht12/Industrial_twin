import pytest
from pathlib import Path
import joblib
from ml.generate_dataset import generate_industrial_dataset
from ml.train_model import train_isolation_forest, FEATURE_COLUMNS

def test_model_training_and_artifacts(tmp_path: Path):
    # 1. Generate small temp dataset
    dataset_path = tmp_path / "test_dataset.csv"
    generate_industrial_dataset(num_samples=200, seed=42, output_path=dataset_path)
    
    model_path = tmp_path / "model.joblib"
    metadata_path = tmp_path / "metadata.json"
    
    # 2. Train model
    metadata = train_isolation_forest(
        dataset_path=dataset_path,
        model_output_path=model_path,
        metadata_output_path=metadata_path,
        seed=42
    )
    
    assert model_path.exists()
    assert metadata_path.exists()
    assert metadata["model_version"] == "1.0.0"
    assert "evaluation_metrics" in metadata
    
    # 3. Inspect saved artifact
    artifact = joblib.load(model_path)
    assert "scaler" in artifact
    assert "model" in artifact
    assert artifact["feature_columns"] == FEATURE_COLUMNS
