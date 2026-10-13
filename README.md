# IndustrialTwin — Industrial Equipment Health Monitoring

An IoT and Machine Learning-based Digital Twin platform designed to monitor industrial motor health, visualize real-time telemetry, identify abnormal operating conditions, and support predictive maintenance.

## Overview

IndustrialTwin creates a software-based digital representation of industrial equipment. It receives motor telemetry from a simulator or a compatible IoT device, processes the data through a backend monitoring pipeline, and displays equipment status through an interactive 3D dashboard.

The project aims to help identify abnormal temperature, vibration, speed, and electrical readings before they lead to equipment failure.

## Key Features

- **3D Digital Twin Dashboard:** Interactive motor visualization using React and Three.js.
- **Real-Time Telemetry:** Motor sensor data delivered through MQTT and WebSocket communication.
- **Machine Health Index:** Health score and status indicators based on equipment telemetry.
- **Anomaly Detection:** Machine learning-based detection of unusual operating patterns.
- **Fault Simulation:** Simulated operating conditions for testing monitoring behavior.
- **Telemetry Storage:** MongoDB integration for storing equipment readings.
- **REST API:** FastAPI backend with API documentation.
- **ESP32 Integration:** Firmware and sensor integration planned for physical-device testing.
- **Monitoring:** Grafana integration for operational monitoring.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| 3D Visualization | Three.js |
| Backend | Python, FastAPI |
| Communication | MQTT, WebSockets |
| Database | MongoDB |
| Machine Learning | Scikit-learn, Isolation Forest |
| Monitoring | Grafana |
| Hardware Prototype | ESP32, MPU6050, DS18B20 |
| Testing | Pytest, Vitest |

## System Architecture

```text
Motor Simulator / ESP32 Sensors
              |
              v
          MQTT Broker
              |
              v
       FastAPI Backend
          /       \
         v         v
     MongoDB    ML / Health Scoring
                    |
                    v
              WebSocket API
                    |
                    v
          React + Three.js UI
```

The simulator generates sample motor telemetry for software testing. Physical ESP32 sensor integration requires compatible hardware and validation.

## Telemetry Parameters

The platform is designed to work with motor parameters such as:

- Temperature
- Vibration RMS and peak
- Shaft speed (RPM)
- Current draw
- Voltage
- Mechanical load
- Operating state

## Getting Started

### Prerequisites

Install the following before running the project:

- Python compatible with the backend environment
- Node.js and npm
- MongoDB
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Industrial_twin.git
cd Industrial_twin
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Configure environment variables

Create a local `.env` file using the project's environment template, if provided. Configure the MongoDB connection, MQTT broker, backend settings, and other required values.

Do not commit real passwords, API keys, or private secrets.

### 3. Start the MQTT broker

Open a terminal in the project root:

```powershell
.\backend\venv\Scripts\python.exe broker_service.py
```

If you cloned the repository on a new machine, create and configure the Python virtual environment and install the project's backend dependencies first.

### 4. Start the backend

Open a second terminal:

```powershell
cd backend
.\venv\Scripts\python.exe -m app.main
```

Backend API: http://localhost:8000

API documentation: http://localhost:8000/docs

### 5. Start the frontend

Open a third terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in the terminal. In the current development setup, the frontend runs at:

http://localhost:3000

### 6. Start the motor simulator

Open a fourth terminal in the project root:

```powershell
.\backend\venv\Scripts\python.exe -m simulator.main --demo --interval 1.0
```

This generates simulated motor telemetry at approximately one-second intervals for development and demonstration.

**Note:** The commands above assume the project's virtual environment and configuration are already set up. On a fresh installation, install the backend dependencies and configure MongoDB and MQTT before starting the services.

## MQTT Topics

| Purpose | Topic |
|---|---|
| Motor telemetry | `industrial/motor/+/telemetry` |
| Motor alerts | `industrial/motor/+/alerts` |
| Motor control | `industrial/motor/+/control` |

## Example Telemetry Payload

```json
{
  "motor_id": "esp32-motor-01",
  "temperature": 45.5,
  "vibration_rms": 1.25,
  "vibration_peak": 0.85,
  "rpm": 1480.0,
  "current_draw": 28.5,
  "voltage": 400.0,
  "load_percentage": 75.0,
  "operating_state": "NORMAL"
}
```

Values are illustrative sample data, not measurements from a real industrial motor.

## Project Status

- Software dashboard and 3D visualization: implemented.
- MQTT and FastAPI telemetry pipeline: implemented and tested in the development environment.
- MongoDB integration: implemented.
- ML anomaly detection and health scoring: included in the software pipeline.
- Simulator-based demonstration: available.
- Physical ESP32 and sensor validation: pending hardware testing.

## Future Improvements

- Validate telemetry with physical sensors and an ESP32.
- Evaluate anomaly detection with real-world motor datasets.
- Improve alerting and historical trend analysis.
- Add secure device provisioning and authenticated communication.
- Validate the system under real equipment operating conditions.

## Disclaimer

IndustrialTwin is a development and monitoring prototype. Simulator results and ML predictions are not a substitute for certified industrial safety systems or professional equipment diagnostics. Do not connect development hardware directly to hazardous motor power circuits.

## Author

**Abhay Singh Bisht**

GitHub: https://github.com/YOUR_USERNAME

