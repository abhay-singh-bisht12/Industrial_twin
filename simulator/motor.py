from enum import Enum
from datetime import datetime, timezone
import random
import math
from typing import Dict, Any, Optional
from simulator.config import sim_settings

class MotorState(str, Enum):
    NORMAL = "NORMAL"
    OVERHEATING = "OVERHEATING"
    BEARING_WEAR = "BEARING_WEAR"
    ELECTRICAL_FAULT = "ELECTRICAL_FAULT"

class MotorSimulator:
    """
    Physics-based time-series telemetry generator for an industrial 3-phase electric motor.
    Includes state machine supporting normal operations and fault injection modes.
    """
    def __init__(
        self,
        motor_id: Optional[str] = None,
        initial_state: MotorState = MotorState.NORMAL,
        seed: Optional[int] = None
    ):
        self.motor_id = motor_id or sim_settings.MOTOR_ID
        self.state = initial_state
        self.load_percentage = sim_settings.BASE_LOAD_PCT
        
        # Internal thermal & mechanical physics state variables
        self.temperature = sim_settings.BASE_TEMPERATURE_C
        self.vibration_rms = sim_settings.BASE_VIBRATION_RMS_MM_S
        self.vibration_peak = sim_settings.BASE_VIBRATION_PEAK_G
        self.current_draw = sim_settings.BASE_CURRENT_DRAW_A
        self.voltage = sim_settings.BASE_VOLTAGE_V
        self.rpm = sim_settings.MOTOR_RATED_SPEED_RPM
        
        # Simulation step time counter
        self._elapsed_time = 0.0
        
        if seed is not None:
            self._rng = random.Random(seed)
        else:
            self._rng = random.Random()

    def set_state(self, new_state: MotorState):
        """Set the operating state of the motor."""
        if isinstance(new_state, str):
            new_state = MotorState(new_state.upper())
        self.state = new_state

    def set_load(self, load_pct: float):
        """Set the mechanical load percentage (0% to 125%)."""
        self.load_percentage = max(0.0, min(125.0, load_pct))

    def step(self, dt: float = 1.0) -> Dict[str, Any]:
        """
        Advance physics simulation by dt seconds and return current telemetry snapshot.
        """
        self._elapsed_time += dt
        
        # Load factor scaling
        load_factor = self.load_percentage / 100.0
        
        # 1. Temperature Physics (First-order thermal response + state escalation)
        target_temp = sim_settings.BASE_TEMPERATURE_C + (load_factor * 12.0)
        if self.state == MotorState.OVERHEATING:
            target_temp = sim_settings.OVERHEATING_TEMP_C + (load_factor * 10.0)
        elif self.state == MotorState.ELECTRICAL_FAULT:
            target_temp = sim_settings.BASE_TEMPERATURE_C + 25.0
            
        # Smooth thermal inertia curve: T(t+dt) = T(t) + (target - T(t)) * (1 - e^(-dt/tau))
        thermal_tau = 30.0  # 30-second thermal time constant
        temp_decay = 1.0 - math.exp(-dt / thermal_tau)
        self.temperature += (target_temp - self.temperature) * temp_decay
        self.temperature += self._rng.gauss(0.0, 0.15)  # Sensor noise
        
        # 2. Vibration Physics (RMS & Peak)
        target_vib_rms = sim_settings.BASE_VIBRATION_RMS_MM_S + (load_factor * 0.5)
        target_vib_peak = sim_settings.BASE_VIBRATION_PEAK_G + (load_factor * 0.3)
        
        if self.state == MotorState.BEARING_WEAR:
            target_vib_rms = sim_settings.BEARING_WEAR_VIBRATION_RMS
            target_vib_peak = sim_settings.BEARING_WEAR_VIBRATION_PEAK
            
        vib_tau = 5.0
        vib_decay = 1.0 - math.exp(-dt / vib_tau)
        self.vibration_rms += (target_vib_rms - self.vibration_rms) * vib_decay + self._rng.gauss(0.0, 0.05)
        self.vibration_peak += (target_vib_peak - self.vibration_peak) * vib_decay + self._rng.gauss(0.0, 0.08)
        
        # High-frequency impact spikes for bearing fault
        if self.state == MotorState.BEARING_WEAR and self._rng.random() < 0.35:
            self.vibration_peak += self._rng.uniform(1.0, 2.5)

        # 3. Voltage Physics
        target_voltage = sim_settings.BASE_VOLTAGE_V
        if self.state == MotorState.ELECTRICAL_FAULT:
            target_voltage = sim_settings.ELECTRICAL_FAULT_VOLTAGE_V  # Voltage sag
            
        self.voltage = target_voltage + self._rng.gauss(0.0, 1.2)

        # 4. Current Draw Physics (Amperes)
        # Power formula: I = (Load_kW * 1000) / (sqrt(3) * V * PF * Efficiency)
        pf = 0.85
        eff = 0.92
        power_w = (sim_settings.MOTOR_RATED_POWER_KW * load_factor) * 1000.0
        calculated_current = power_w / (math.sqrt(3) * max(self.voltage, 100.0) * pf * eff)
        
        if self.state == MotorState.ELECTRICAL_FAULT:
            calculated_current = sim_settings.ELECTRICAL_FAULT_CURRENT_A  # Current spike under phase fault
            
        self.current_draw = calculated_current + self._rng.gauss(0.0, 0.3)

        # 5. RPM Physics (Induction motor slip under load)
        # Synchronous speed = 1500 RPM, slip increases with load
        slip = 0.02 * load_factor
        if self.state == MotorState.BEARING_WEAR:
            slip += 0.015  # Mechanical friction loss
            
        target_rpm = sim_settings.MOTOR_RATED_SPEED_RPM * (1.0 - slip)
        self.rpm = target_rpm + self._rng.gauss(0.0, 2.0)

        # Ensure valid lower bounds
        self.temperature = max(0.0, round(self.temperature, 2))
        self.vibration_rms = max(0.0, round(self.vibration_rms, 2))
        self.vibration_peak = max(0.0, round(self.vibration_peak, 2))
        self.current_draw = max(0.0, round(self.current_draw, 2))
        self.voltage = max(0.0, round(self.voltage, 2))
        self.rpm = max(0.0, round(self.rpm, 1))

        return {
            "motor_id": self.motor_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": self.temperature,
            "vibration_rms": self.vibration_rms,
            "vibration_peak": self.vibration_peak,
            "rpm": self.rpm,
            "current_draw": self.current_draw,
            "voltage": self.voltage,
            "load_percentage": round(self.load_percentage, 1),
            "operating_state": self.state.value
        }
