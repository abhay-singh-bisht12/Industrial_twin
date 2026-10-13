# ESP32 & Physical Industrial Sensor Integration Guide

This guide documents how to connect a physical **ESP32 microcontroller** equipped with industrial sensors (MPU6050 vibration sensor and DS18B20 temperature sensor) to publish real-time telemetry over MQTT to the **IndustrialTwin** health monitoring platform.

---

## 🏗️ Hardware Architecture & Data Pipeline

```
 +-----------------------------------------------------------------------------------+
 |                             ESP32 Physical Hardware                               |
 |  +--------------------+  +-------------------+  +------------------------------+  |
 |  | MPU6050 Vibration  |  | DS18B20 Temp      |  | SCT-013 / ZMPT (Optional)    |  |
 |  | (I2C: GPIO 21/22)  |  | (OneWire: GPIO 4) |  | (Analog: GPIO 34/35)         |  |
 |  +---------+----------+  +---------+---------+  +--------------+---------------+  |
 |            |                       |                           |                  |
 |            +-----------------------+---------------------------+                  |
 |                                    v                                              |
 |                           ESP32 Microcontroller                                   |
 |                   (FreeRTOS + WiFi + PubSubClient MQTT)                           |
 +------------------------------------+----------------------------------------------+
                                      |
                         (MQTT JSON Telemetry Topic)
                         industrial/motor/{MOTOR_ID}/telemetry
                                      v
 +------------------------------------+----------------------------------------------+
 |                             IndustrialTwin Platform                               |
 |   Mosquitto MQTT ➔ FastAPI Ingestion ➔ MongoDB ➔ ML Engine ➔ React UI / Grafana  |
 +-----------------------------------------------------------------------------------+
```

---

## 🔌 Text Wiring Diagram & Pin Mapping

```
     +-------------------------------------------------------------+
     |                       ESP32 DEVKIT V1                       |
     |                                                             |
     |  [ 3.3V ] ----------------+-----------------+               |
     |  [  GND ] ----------+     |                 |               |
     |                     |     |                 |               |
     |  [GPIO 21] (SDA) ---|-----|----+            |               |
     |  [GPIO 22] (SCL) ---|-----|----+|           |               |
     |                     |     |    ||           |               |
     |  [GPIO 4 ] (Data) --|-----|----||-----+     |               |
     +---------------------|-----|----||-----|-----|---------------+
                           |     |    ||     |     |
                           |     |    ||     +--[ 4.7kΩ Resistor ]--+ (Pullup)
                           |     |    ||     |
                      +----+-----+----+|-----+----+
                      |     MPU6050 Sensor        |
                      | VCC  GND  SDA  SCL        |
                      +---------------------------+

                      +---------------------------+
                      |     DS18B20 Sensor        |
                      | VCC  GND  DATA            |
                      +---------------------------+
```

### Pin Map Table:

| Sensor Module | Parameter Measured | ESP32 Pin Connection | Protocol / Library |
|---|---|---|---|
| **MPU6050** | Vibration RMS (mm/s) & Peak Acceleration (g) | SDA: `GPIO 21`, SCL: `GPIO 22` | I2C (`Adafruit_MPU6050`) |
| **DS18B20** | Motor Casing Surface Temperature (°C) | Data: `GPIO 4` (4.7kΩ pullup to 3.3V) | OneWire / DallasTemperature |
| **SCT-013-000 (Optional)** | Phase Current Draw (RMS Amperes) | Analog: `GPIO 34` | Analog ADC (`EmonLib`) |
| **ZMPT101B (Optional)** | Line Voltage (RMS Volts) | Analog: `GPIO 35` | Analog ADC |
| **Hall Sensor (Optional)** | Motor Shaft Speed (RPM) | Interrupt: `GPIO 18` | Hardware Interrupt (`attachInterrupt`) |

---

## 📚 Required Arduino IDE Libraries

Install the following libraries via the Arduino IDE Library Manager (`Ctrl + Shift + I`):

1. **`WiFi`**: Included with official ESP32 Arduino Core board package.
2. **`PubSubClient`**: By Nick O'Leary (v2.8+).
3. **`ArduinoJson`**: By Benoit Blanchon (v6.x or v7.x).
4. **`Adafruit MPU6050`**: By Adafruit.
5. **`Adafruit Unified Sensor`**: By Adafruit.
6. **`OneWire`**: By Jim Studt et al.
7. **`DallasTemperature`**: By Miles Burton.

---

## 📡 MQTT Topic & Payload Specification

### Telemetry Topic:
`industrial/motor/{MOTOR_ID}/telemetry` (e.g., `industrial/motor/esp32-motor-01/telemetry`)

### Control Topic (Fault Injection Callback):
`industrial/motor/{MOTOR_ID}/control` (e.g., `industrial/motor/esp32-motor-01/control`)

### Expected JSON Telemetry Payload (Strict Pydantic Contract):
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

> [!NOTE]
> **Handling Unmeasured Parameters**: If physical current (SCT-013) or voltage (ZMPT101B) sensors are not physically attached, the firmware outputs stable nominal defaults (`28.5A`, `400.0V`, `1480.0 RPM`, `75.0% Load`) to adhere to the backend `TelemetryPayload` validation schema without causing contract errors.

---

## ⚡ Flashing & Upload Instructions

1. Open Arduino IDE or PlatformIO.
2. Select Board: **`ESP32 Dev Module`**.
3. Open [`hardware/esp32_industrial_twin.ino`](file:///d:/IndustrialTwin/hardware/esp32_industrial_twin.ino).
4. Update configuration constants in lines 16–22:
   ```cpp
   const char* WIFI_SSID       = "YOUR_WIFI_SSID";
   const char* WIFI_PASS       = "YOUR_WIFI_PASSWORD";
   const char* MQTT_BROKER_IP  = "192.168.1.100"; // Host IP address running Mosquitto
   ```
5. Connect ESP32 to PC via Micro-USB or USB-C cable. Select COM port.
6. Click **Upload** (`Ctrl + U`).
7. Open Serial Monitor (`115200 baud`) to inspect startup, Wi-Fi connection, MPU6050 detection, and MQTT publish logs.

---

## 🚀 How to Run the Complete IndustrialTwin Stack with ESP32

1. **Start Mosquitto MQTT Broker**:
   ```powershell
   .\backend\venv\Scripts\python.exe broker_service.py
   ```
2. **Start FastAPI Backend Engine**:
   ```powershell
   cd backend
   .\venv\Scripts\python.exe -m app.main
   ```
3. **Start React Digital Twin Web UI**:
   ```powershell
   cd frontend
   npm run dev
   ```
4. **Power on ESP32**:
   - The ESP32 will connect to Wi-Fi, connect to Mosquitto, publish sensor telemetry every 1 second, and listen on `industrial/motor/esp32-motor-01/control` for fault injection commands sent from the React UI!

