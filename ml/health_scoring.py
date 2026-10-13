import math
from typing import Dict, Any, List

def calculate_machine_health(
    temperature: float,
    vibration_rms: float,
    vibration_peak: float,
    current_draw: float,
    voltage: float,
    rpm: float,
    load_percentage: float = 75.0,
    ml_anomaly_score: float = 0.0,
    operating_state: str = "NORMAL"
) -> Dict[str, Any]:
    """
    Computes a deterministic 0 - 100 Machine Health Score combining physics boundary rules
    and Machine Learning Isolation Forest anomaly scores.
    """
    degradation_reasons: List[str] = []
    
    # 1. Thermal Degradation Penalty (Base: 45°C - 65°C normal)
    thermal_penalty = 0.0
    if temperature > 85.0:
        thermal_penalty = min(50.0, 25.0 + (temperature - 85.0) * 2.5)
        degradation_reasons.append(f"Critical motor temperature: {temperature:.1f}°C (> 85°C threshold)")
    elif temperature > 65.0:
        thermal_penalty = (temperature - 65.0) * 1.25
        degradation_reasons.append(f"Elevated motor temperature: {temperature:.1f}°C (Warning range 65-85°C)")
        
    # 2. Vibration Degradation Penalty (Base: RMS <= 2.8 mm/s, Peak <= 1.8 g)
    vibration_penalty = 0.0
    if vibration_rms > 4.5:
        vib_sub = min(35.0, 15.0 + (vibration_rms - 4.5) * 8.0)
        vibration_penalty += vib_sub
        degradation_reasons.append(f"Severe mechanical vibration RMS: {vibration_rms:.2f} mm/s (> 4.5 mm/s limit)")
    elif vibration_rms > 2.8:
        vib_sub = (vibration_rms - 2.8) * 8.8
        vibration_penalty += vib_sub
        degradation_reasons.append(f"Elevated vibration RMS: {vibration_rms:.2f} mm/s (Warning range 2.8-4.5 mm/s)")

    if vibration_peak > 3.0:
        peak_sub = min(20.0, 10.0 + (vibration_peak - 3.0) * 5.0)
        vibration_penalty += peak_sub
        degradation_reasons.append(f"High bearing impact peak: {vibration_peak:.2f} g (> 3.0 g limit)")

    vibration_penalty = min(50.0, vibration_penalty)

    # 3. Electrical & Current Penalty (Base: Current <= 35A, Voltage >= 380V)
    electrical_penalty = 0.0
    if current_draw > 45.0:
        electrical_penalty += min(30.0, 15.0 + (current_draw - 45.0) * 1.5)
        degradation_reasons.append(f"Current surge: {current_draw:.1f} A (> 45 A fault threshold)")
    elif current_draw > 35.0 and load_percentage <= 80.0:
        electrical_penalty += (current_draw - 35.0) * 1.2
        degradation_reasons.append(f"Unusual current draw: {current_draw:.1f} A under {load_percentage:.0f}% load")

    if voltage < 370.0:
        electrical_penalty += min(20.0, (370.0 - voltage) * 1.0)
        degradation_reasons.append(f"Supply voltage sag: {voltage:.1f} V (< 370 V threshold)")

    electrical_penalty = min(40.0, electrical_penalty)

    # 4. RPM Slip Penalty
    rpm_penalty = 0.0
    if rpm < 1400.0:
        rpm_penalty = min(20.0, (1400.0 - rpm) * 0.2)
        degradation_reasons.append(f"Excessive speed slip: {rpm:.0f} RPM (< 1400 RPM minimum)")

    # Compute Rule-based Sensor Health Score
    sensor_total_penalty = thermal_penalty + vibration_penalty + electrical_penalty + rpm_penalty
    sensor_health_score = max(0.0, min(100.0, 100.0 - sensor_total_penalty))

    # 5. Machine Learning Anomaly Score Penalty (0.0 to 1.0 scale)
    ml_penalty = 0.0
    if ml_anomaly_score > 0.65:
        ml_penalty = min(30.0, (ml_anomaly_score - 0.65) * 85.0)
        degradation_reasons.append(f"ML Anomaly Model detected abnormal telemetry pattern (Score: {ml_anomaly_score:.2f})")

    # Composite Health Score
    composite_health_score = max(0.0, min(100.0, sensor_health_score - ml_penalty))

    # Determine Health Tier
    if composite_health_score >= 80.0:
        health_tier = "HEALTHY"
    elif composite_health_score >= 50.0:
        health_tier = "WARNING"
    else:
        health_tier = "CRITICAL"

    if not degradation_reasons:
        degradation_reasons.append("All motor telemetry parameters operating within normal physics boundaries.")

    return {
        "sensor_health_score": round(sensor_health_score, 1),
        "ml_anomaly_score": round(ml_anomaly_score, 4),
        "composite_health_score": round(composite_health_score, 1),
        "health_tier": health_tier,
        "is_anomaly": bool(ml_anomaly_score > 0.65 or health_tier == "CRITICAL"),
        "degradation_reasons": degradation_reasons,
        "penalty_breakdown": {
            "thermal": round(thermal_penalty, 1),
            "vibration": round(vibration_penalty, 1),
            "electrical": round(electrical_penalty, 1),
            "rpm_slip": round(rpm_penalty, 1),
            "ml_anomaly": round(ml_penalty, 1)
        }
    }
