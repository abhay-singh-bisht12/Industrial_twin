import argparse
import logging
from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np
from simulator.motor import MotorSimulator, MotorState

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [dataset_generator]: %(message)s")
logger = logging.getLogger("dataset_generator")

def generate_industrial_dataset(
    num_samples: int = 10000,
    motor_id: str = "motor-01",
    seed: int = 42,
    output_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Generates a reproducible synthetic industrial motor telemetry dataset.
    Simulates operating behavior, dynamic mechanical loads, and progressive fault escalations.
    """
    logger.info(f"Generating synthetic industrial dataset with {num_samples} samples (Seed: {seed}, Motor: {motor_id})...")
    
    rng = np.random.default_rng(seed)
    records = []
    
    # Instantiate motor simulator with seed
    sim = MotorSimulator(motor_id=motor_id, seed=seed)
    
    # State distribution allocation
    # 70% Normal, 10% Overheating, 10% Bearing Wear, 10% Electrical Fault
    state_sequence = [
        (MotorState.NORMAL, int(num_samples * 0.70)),
        (MotorState.OVERHEATING, int(num_samples * 0.10)),
        (MotorState.BEARING_WEAR, int(num_samples * 0.10)),
        (MotorState.ELECTRICAL_FAULT, int(num_samples * 0.10))
    ]
    
    total_generated = 0
    for state, count in state_sequence:
        sim.set_state(state)
        for _ in range(count):
            # Vary load dynamically between 40% and 115%
            if rng.random() < 0.05:
                sim.set_load(float(rng.uniform(40.0, 115.0)))
                
            sample = sim.step(dt=1.0)
            
            # Add metadata tag indicating synthetic simulation data
            sample["data_type"] = "SYNTHETIC_SIMULATED"
            records.append(sample)
            total_generated += 1
            
            if total_generated >= num_samples:
                break
        if total_generated >= num_samples:
            break

    df = pd.DataFrame(records)
    logger.info(f"Successfully generated {len(df)} telemetry records.")
    logger.info(f"State breakdown:\n{df['operating_state'].value_counts()}")

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Dataset saved to {output_path}")

    return df

def main():
    parser = argparse.ArgumentParser(description="Generate Synthetic Motor Telemetry Dataset")
    parser.add_argument("--samples", type=int, default=10000, help="Number of telemetry samples")
    parser.add_argument("--motor-id", type=str, default="motor-01", help="Motor ID")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, default="ml/data/motor_telemetry_dataset.csv", help="Output CSV path")

    args = parser.parse_args()
    out_path = Path(args.output)
    generate_industrial_dataset(num_samples=args.samples, motor_id=args.motor_id, seed=args.seed, output_path=out_path)

if __name__ == "__main__":
    main()
