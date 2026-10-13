import argparse
import logging
import signal
import sys
import time
from typing import Dict, Any

from simulator.config import sim_settings
from simulator.motor import MotorSimulator, MotorState
from simulator.mqtt_client import MotorMQTTClient

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [simulator]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("simulator")

running = True

def signal_handler(sig, frame):
    global running
    logger.info("Termination signal received. Shutting down motor simulator...")
    running = False

def main():
    global running
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description="Industrial Twin - Motor Telemetry Simulator")
    parser.add_argument("--motor-id", type=str, default=sim_settings.MOTOR_ID, help="Motor ID")
    parser.add_argument("--interval", type=float, default=sim_settings.PUBLISH_INTERVAL_SEC, help="Publish interval in seconds")
    parser.add_argument("--state", type=str, default="NORMAL", choices=["NORMAL", "OVERHEATING", "BEARING_WEAR", "ELECTRICAL_FAULT"], help="Initial state")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic simulation mode")
    parser.add_argument("--demo", action="store_true", help="Run automated demo sequence cycling through states")

    args = parser.parse_args()

    motor = MotorSimulator(
        motor_id=args.motor_id,
        initial_state=MotorState(args.state),
        seed=args.seed
    )
    
    mqtt_client = MotorMQTTClient(motor_id=args.motor_id)
    
    def handle_control(command: Dict[str, Any]):
        if "state" in command:
            new_state = command["state"].upper()
            try:
                motor.set_state(new_state)
                logger.info(f"Control command applied: Changed motor state to {new_state}")
            except Exception as e:
                logger.error(f"Invalid state in control command '{new_state}': {e}")
        if "load_percentage" in command:
            motor.set_load(float(command["load_percentage"]))
            logger.info(f"Control command applied: Changed motor load to {command['load_percentage']}%")

    mqtt_client.set_control_callback(handle_control)
    connected = mqtt_client.connect()
    
    if not connected:
        logger.warning("Starting simulator in STANDALONE mode (MQTT broker not reachable). Telemetry will be printed locally.")

    logger.info(f"Motor Simulator running for motor '{args.motor_id}' in state '{args.state}' (Interval: {args.interval}s)")

    step_count = 0
    demo_states = [MotorState.NORMAL, MotorState.OVERHEATING, MotorState.BEARING_WEAR, MotorState.ELECTRICAL_FAULT]
    demo_index = 0

    try:
        while running:
            # If demo mode enabled, cycle states every 15 steps
            if args.demo and step_count > 0 and step_count % 15 == 0:
                demo_index = (demo_index + 1) % len(demo_states)
                next_state = demo_states[demo_index]
                motor.set_state(next_state)
                logger.info(f"DEMO MODE: Transitioning to {next_state.value}")

            telemetry = motor.step(dt=args.interval)
            
            if connected:
                mqtt_client.publish_telemetry(telemetry)
            else:
                logger.info(f"[LOCAL TELEMETRY] Temp: {telemetry['temperature']}°C | Vib: {telemetry['vibration_rms']}mm/s | Current: {telemetry['current_draw']}A | State: {telemetry['operating_state']}")

            step_count += 1
            time.sleep(args.interval)

    finally:
        mqtt_client.disconnect()
        logger.info("Motor simulator exited cleanly.")

if __name__ == "__main__":
    main()
