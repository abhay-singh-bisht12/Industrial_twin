# IndustrialTwin - Digital Twin for Industrial Equipment Health Monitoring

**IndustrialTwin** is an end-to-end industrial equipment health monitoring platform featuring a physics-based motor telemetry simulator, MQTT message broker, FastAPI ingestion service, MongoDB time-series storage, scikit-learn ML anomaly detection & composite health scoring, Grafana dashboards, and an interactive 2D/3D Digital Twin web UI.

---

## 🏗️ System Architecture

```
 +-----------------------------------------------------------------------------------+
 |                                   IoT Telemetry                                   |
 |  +--------------------------+                      +---------------------------+  |
 |  | Python Motor Simulator   | ---(MQTT Telemetry)->| Eclipse Mosquitto Broker  |  |
 |  | (Physics & Fault Engine) |                      | (Ports 1883 / 9001 WS)    |  |
 |  +--------------------------+                      +-------------+-------------+  |
 +------------------------------------------------------------------|----------------+
                                                                    |
                                                                (Publish)
                                                                    v
 +------------------------------------------------------------------|----------------+
 |                                  Backend & ML Engine             |                |
 |  +---------------------------------------------------------------+-------------+  |
 |  |                        FastAPI Application                                  |  |
 |  |  +---------------------+   +---------------------+   +-------------------+  |  |
 |  |  | MQTT Consumer Task  |-->| ML Inference Engine |-->| WebSocket Server  |  |  |
 |  |  | (Schema Validation) |   | (IsolationForest &  |   | (Realtime Stream) |  |  |
 |  |  +----------+----------+   | Health Scoring)     |   +---------+---------+  |  |
 |  |             |              +----------+----------+             |            |  |
 |  +-------------|-------------------------|------------------------|------------+  |
 |                v                         v                        v               |
 |       +------------------------------------------------------------------+        |
 |       |                       MongoDB Database                           |        |
 |       |            (Telemetry Snapshots & Anomaly Alerts)                |        |
 |       +------------------------------------------------------------------+        |
 +-----------------------------------------------------------------------------------+
```

---

## 🤖 Machine Learning & Health Scoring Engine (Phase 3)

### 1. Synthetic Dataset Generator
Generated via `ml/generate_dataset.py` with reproducible seed physics simulation across dynamic mechanical load profiles (40% to 115% load).
- **Distribution**: 70% Normal, 10% Overheating, 10% Bearing Wear, 10% Electrical Fault.
- **Dataset Location**: `ml/data/motor_telemetry_dataset.csv`.

```powershell
.\backend\venv\Scripts\python.exe -m ml.generate_dataset --samples 10000 --seed 42
```

### 2. ML Model Training & Pipeline
Trained via `ml/train_model.py` using **Isolation Forest** on scaled features (`StandardScaler`).
- **Extracted Features**: `temperature`, `vibration_rms`, `vibration_peak`, `rpm`, `current_draw`, `voltage`, `load_percentage`, `power_factor_approx`, `vibration_crest_factor`.
- **Evaluation Metrics (Hold-out Test Set)**:
  - **ROC-AUC**: `0.9249`
  - **Accuracy**: `79.45%`
- **Artifacts Saved**: `ml/models/health_model.joblib` and `ml/models/model_metadata.json`.

```powershell
.\backend\venv\Scripts\python.exe -m ml.train_model --seed 42
```

### 3. Composite Machine Health Scoring Engine (`0 - 100`)
Computes composite health score:

$$\text{Composite Health} = 100 - (\text{Thermal Penalty} + \text{Vibration Penalty} + \text{Electrical Penalty} + \text{RPM Slip Penalty} + \text{ML Anomaly Penalty})$$

#### Health Tiers:
- **HEALTHY** (Score $\ge 80.0$)
- **WARNING** (Score $50.0 - 79.9$)
- **CRITICAL** (Score $< 50.0$)

### 4. Digital Twin Frontend (Phase 4)
- **Interactive 2D & 3D Web Dashboard**: Built with React, Vite, Tailwind CSS, Lucide Icons, and Three.js.
- **3D Motor Renderer (`MotorDigitalTwin3D.jsx`)**: Real-time 3D visualization of motor status with dynamic rotation speeds, thermal glow shaders, fault particle effects, and status lighting.
- **Live WebSocket Feed & State Controls**: Real-time telemetry gauge updates, sparkline time-series trends, ML anomaly score alerts, and direct UI fault mode injection buttons.

### 5. Production Packaging & Grafana Provisioning (Phase 5)
- **Grafana Dashboard Provisioning**: Automated datasource (`datasources.yml`) and dashboard (`industrial_twin.json`) provisioning for operations teams monitoring real-time telemetry, ML scores, and alerts.
- **Docker Compose Orchestration**: Containerized setup for `mosquitto`, `mongodb`, `backend`, `frontend`, and `grafana` with health checks and volume persistence.

### 6. Physical ESP32 Sensor Integration (Phase 6)
- **Physical Sensor Hardware Integration**: Production C++ firmware (`hardware/esp32_industrial_twin.ino`) and complete connection guide (`hardware/ESP32_SENSOR_GUIDE.md`) for real ESP32 microcontrollers with MPU6050 vibration/acceleration and DS18B20 surface temperature sensors.
- **Auto-Reconnect & Telemetry Protocol**: Includes Wi-Fi and MQTT auto-reconnect handling, serial debugging logs, MQTT control callback for remote state injection, and 100% Pydantic-compliant telemetry payload delivery over `industrial/motor/{MOTOR_ID}/telemetry`.

---

## 📡 API Endpoints

### ML & Machine Health Endpoints (`/api/v1/ml/`)
- `GET /api/v1/ml/health?motor_id=motor-01`: Current machine health evaluation, tier, degradation reasons, and penalty breakdown.
- `GET /api/v1/ml/health/history?motor_id=motor-01&limit=50`: Historical health score time-series data.
- `GET /api/v1/ml/anomalies`: Logged anomaly alert records.
- `GET /api/v1/ml/model-info`: Active ML model metadata, versioning, feature list, and evaluation metrics.

### Telemetry Endpoints (`/api/v1/telemetry/`)
- `GET /api/v1/telemetry/recent?motor_id=motor-01&limit=50`: Recent telemetry snapshots.
- `GET /api/v1/telemetry/status?motor_id=motor-01`: Motor operational status summary.
- `GET /api/v1/telemetry/stats`: Metric averages and max values over configurable time window.
- `POST /api/v1/telemetry/control`: Send control action to simulator via MQTT.
- `WS /api/v1/ws/telemetry`: Live WebSocket streaming endpoint.

---

## 🚀 How to Run the Complete System

### Option A: Local Development Setup (Windows)

#### 1. Run Complete Automated Test Suite (39 Tests Total: 36 Python + 3 Vitest)
```powershell
# Python Tests (Backend, ML, Simulator & ESP32 Schema Compatibility)
.\backend\venv\Scripts\python.exe -m pytest

# Frontend Tests (React / Vitest)
cd frontend
npm test
```

#### 2. Start Embedded MQTT Broker (Ports 1883 TCP / 9001 WebSockets)
```powershell
.\backend\venv\Scripts\python.exe broker_service.py
```

#### 3. Start FastAPI Backend Service
```powershell
cd backend
.\venv\Scripts\python.exe -m app.main
```

#### 4. Start React Digital Twin Dashboard
```powershell
cd frontend
npm run dev
```

#### 5. Run Motor Telemetry Simulator (Demo Mode)
```powershell
.\backend\venv\Scripts\python.exe -m simulator.main --demo --interval 1.0
```

---

### Option B: Production Docker Compose Deployment

Launch all services (Mosquitto MQTT, MongoDB, FastAPI Backend, React Frontend, Grafana):
```bash
docker-compose up --build -d
```

- **Digital Twin UI**: `http://localhost:3000`
- **FastAPI Documentation**: `http://localhost:8000/docs`
- **Grafana Monitoring Dashboard**: `http://localhost:3001` (Credentials: `admin`/`admin_secure_password`)
- **MQTT Broker**: Ports `1883` (TCP) and `9001` (WebSockets)

---

## 🛠️ Physical ESP32 Hardware Integration

To switch from the software simulator to real industrial sensors:
1. Refer to [hardware/ESP32_SENSOR_GUIDE.md](file:///d:/IndustrialTwin/hardware/ESP32_SENSOR_GUIDE.md) for pinout mappings and text wiring diagrams.
2. Flash [hardware/esp32_industrial_twin.ino](file:///d:/IndustrialTwin/hardware/esp32_industrial_twin.ino) onto an ESP32 microcontroller using Arduino IDE or PlatformIO.
3. Configure Wi-Fi credentials (`WIFI_SSID`, `WIFI_PASS`) and MQTT broker IP address (`MQTT_BROKER_IP`).
4. Telemetry from physical MPU6050 and DS18B20 sensors will flow seamlessly into the backend, ML engine, Digital Twin UI, and Grafana dashboard.

---

## ⚠️ Known Limitations
- **Synthetic Data Disclaimer**: Model evaluation metrics reflect simulation behavior and verify end-to-end pipeline mechanics. Real-world predictive maintenance deployment requires training on physical sensor data from actual motor degradation trials.
