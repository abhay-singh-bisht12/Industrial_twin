import pytest
from ml.health_scoring import calculate_machine_health

def test_health_scoring_normal_telemetry():
    res = calculate_machine_health(
        temperature=48.0,
        vibration_rms=1.2,
        vibration_peak=0.8,
        current_draw=28.0,
        voltage=400.0,
        rpm=1480.0,
        load_percentage=75.0,
        ml_anomaly_score=0.10,
        operating_state="NORMAL"
    )
    assert res["composite_health_score"] >= 90.0
    assert res["health_tier"] == "HEALTHY"
    assert res["is_anomaly"] is False
    assert res["penalty_breakdown"]["thermal"] == 0.0
    assert res["penalty_breakdown"]["vibration"] == 0.0

def test_health_scoring_overheating():
    res = calculate_machine_health(
        temperature=92.0,  # Overheating
        vibration_rms=1.5,
        vibration_peak=0.9,
        current_draw=28.0,
        voltage=400.0,
        rpm=1480.0,
        load_percentage=75.0,
        ml_anomaly_score=0.30,
        operating_state="OVERHEATING"
    )
    assert res["composite_health_score"] < 60.0
    assert res["penalty_breakdown"]["thermal"] > 20.0
    assert any("temperature" in r for r in res["degradation_reasons"])

def test_health_scoring_bearing_wear():
    res = calculate_machine_health(
        temperature=50.0,
        vibration_rms=6.5,  # Severe vibration
        vibration_peak=4.2,  # Bearing impact peak
        current_draw=28.0,
        voltage=400.0,
        rpm=1450.0,
        load_percentage=75.0,
        ml_anomaly_score=0.75, # High ML anomaly score
        operating_state="BEARING_WEAR"
    )
    assert res["composite_health_score"] < 50.0
    assert res["health_tier"] == "CRITICAL"
    assert res["is_anomaly"] is True
    assert res["penalty_breakdown"]["vibration"] > 20.0
    assert res["penalty_breakdown"]["ml_anomaly"] > 0.0

def test_health_scoring_bounds():
    # Test boundary limits (never below 0 or above 100)
    res_extreme = calculate_machine_health(
        temperature=200.0,
        vibration_rms=50.0,
        vibration_peak=20.0,
        current_draw=200.0,
        voltage=200.0,
        rpm=500.0,
        ml_anomaly_score=1.0,
        operating_state="ELECTRICAL_FAULT"
    )
    assert res_extreme["composite_health_score"] == 0.0
    assert res_extreme["health_tier"] == "CRITICAL"
