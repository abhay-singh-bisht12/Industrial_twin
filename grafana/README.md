# Grafana Monitoring Setup & Provisioning Guide

**IndustrialTwin** uses Grafana for operational time-series analytics, historical trend tracking, and engineering investigations.

---

## 📊 Dashboard Panels

1. **System Overview**:
   - Total Motor Count
   - Live System Status (Healthy / Degraded)
   - Machine Health Index Gauge (0 - 100%)
   - Isolation Forest Anomaly Score (0.0 - 1.0)

2. **Sensor Telemetry Time-Series**:
   - Temperature vs Time (°C)
   - Vibration Velocity RMS (mm/s) & Impact Peak (g)
   - Shaft Speed (RPM)
   - Phase Current Draw (Amperes) & Voltage (V)

3. **Machine Health & Anomaly History**:
   - Composite Health Score Trend (Last 15m, 1h, 6h, 24h, 7d)
   - Logged Anomaly Events Table

---

## 🚀 Accessing Grafana

- **Local Access**: `http://localhost:3000`
- **Default Credentials**:
  - Username: `admin` (or configured via `${GRAFANA_ADMIN_USER}`)
  - Password: `admin_secure_password` (or configured via `${GRAFANA_ADMIN_PASSWORD}`)
