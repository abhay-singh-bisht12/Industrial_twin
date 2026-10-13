import pytest
from simulator.motor import MotorSimulator, MotorState

def test_motor_initial_state():
    sim = MotorSimulator(motor_id="test-motor-01", initial_state=MotorState.NORMAL, seed=42)
    assert sim.motor_id == "test-motor-01"
    assert sim.state == MotorState.NORMAL
    assert sim.temperature == 45.0
    assert sim.vibration_rms == 1.2

def test_motor_step_normal():
    sim = MotorSimulator(motor_id="test-motor-01", seed=42)
    data = sim.step(dt=1.0)
    assert data["motor_id"] == "test-motor-01"
    assert data["operating_state"] == "NORMAL"
    assert 30.0 <= data["temperature"] <= 60.0
    assert 0.5 <= data["vibration_rms"] <= 3.0
    assert 20.0 <= data["current_draw"] <= 40.0

def test_motor_overheating_state_transition():
    sim = MotorSimulator(seed=100)
    sim.set_state(MotorState.OVERHEATING)
    # Advance time 30 steps to allow thermal curve to ramp up
    for _ in range(30):
        data = sim.step(dt=2.0)
    assert data["temperature"] > 75.0
    assert data["operating_state"] == "OVERHEATING"

def test_motor_bearing_wear_state_transition():
    sim = MotorSimulator(seed=200)
    sim.set_state(MotorState.BEARING_WEAR)
    for _ in range(10):
        data = sim.step(dt=1.0)
    assert data["vibration_rms"] > 3.0
    assert data["operating_state"] == "BEARING_WEAR"

def test_motor_electrical_fault_state_transition():
    sim = MotorSimulator(seed=300)
    sim.set_state(MotorState.ELECTRICAL_FAULT)
    data = sim.step(dt=1.0)
    assert data["current_draw"] > 45.0
    assert data["operating_state"] == "ELECTRICAL_FAULT"

def test_motor_seed_determinism():
    sim1 = MotorSimulator(seed=999)
    sim2 = MotorSimulator(seed=999)
    
    res1 = [sim1.step(dt=1.0) for _ in range(5)]
    res2 = [sim2.step(dt=1.0) for _ in range(5)]
    
    for r1, r2 in zip(res1, res2):
        assert r1["temperature"] == r2["temperature"]
        assert r1["vibration_rms"] == r2["vibration_rms"]
        assert r1["current_draw"] == r2["current_draw"]
