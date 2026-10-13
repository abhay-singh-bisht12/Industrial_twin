import pytest
import pandas as pd
from ml.generate_dataset import generate_industrial_dataset

def test_dataset_generation_reproducibility():
    df1 = generate_industrial_dataset(num_samples=100, seed=42)
    df2 = generate_industrial_dataset(num_samples=100, seed=42)
    
    assert len(df1) == 100
    assert len(df2) == 100
    pd.testing.assert_frame_equal(
        df1.drop(columns=["timestamp"]),
        df2.drop(columns=["timestamp"])
    )

def test_dataset_columns_and_states():
    df = generate_industrial_dataset(num_samples=500, seed=123)
    required_cols = [
        "motor_id", "timestamp", "temperature", "vibration_rms",
        "vibration_peak", "rpm", "current_draw", "voltage",
        "load_percentage", "operating_state", "data_type"
    ]
    for col in required_cols:
        assert col in df.columns
        
    states = set(df["operating_state"].unique())
    assert "NORMAL" in states
    assert "OVERHEATING" in states
    assert "BEARING_WEAR" in states
    assert "ELECTRICAL_FAULT" in states
