import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../services/api';
import { useWebSocket } from './useWebSocket';

const MAX_HISTORY_SAMPLES = 80;

export function useMotorData(initialMotorId = 'motor-01') {
  const [selectedMotor, setSelectedMotor] = useState(initialMotorId);
  const [motorList, setMotorList] = useState(['motor-01', 'motor-02', 'motor-03', 'motor-04']);
  const [currentTelemetry, setCurrentTelemetry] = useState(null);
  const [telemetryHistory, setTelemetryHistory] = useState([]);
  const [healthData, setHealthData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch initial REST data for selected motor
  const loadInitialData = useCallback(async (motorId) => {
    setIsLoading(true);
    try {
      // 1. Fetch available motors
      const motorsRes = await api.getMotorList().catch(() => null);
      if (motorsRes && motorsRes.motors) {
        setMotorList(motorsRes.motors);
      }

      // 2. Fetch recent telemetry history
      const recentRes = await api.getRecentTelemetry(motorId, MAX_HISTORY_SAMPLES).catch(() => null);
      if (recentRes && recentRes.data && recentRes.data.length > 0) {
        const sortedHistory = [...recentRes.data].reverse();
        setTelemetryHistory(sortedHistory);
        setCurrentTelemetry(sortedHistory[sortedHistory.length - 1]);
      } else {
        setTelemetryHistory([]);
      }

      // 3. Fetch Machine Health
      const healthRes = await api.getMachineHealth(motorId).catch(() => null);
      if (healthRes) {
        setHealthData(healthRes);
      }

      // 4. Fetch Anomaly Alerts
      const alertsRes = await api.getAnomalies(motorId, 20).catch(() => null);
      if (alertsRes && alertsRes.alerts) {
        setAlerts(alertsRes.alerts);
      }

      // 5. Fetch Model Metadata
      const modelRes = await api.getModelInfo().catch(() => null);
      if (modelRes) {
        setModelInfo(modelRes);
      }
    } catch (err) {
      console.error('[useMotorData] Initial load error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInitialData(selectedMotor);
  }, [selectedMotor, loadInitialData]);

  // Handle incoming live WebSocket message
  const handleLiveTelemetry = useCallback((data) => {
    // Check if message belongs to currently selected motor
    if (data && data.motor_id === selectedMotor) {
      setCurrentTelemetry(data);

      // Update Health Data from augmented WebSocket message
      if (data.composite_health_score !== undefined) {
        setHealthData({
          motor_id: data.motor_id,
          timestamp: data.timestamp,
          operating_state: data.operating_state,
          composite_health_score: data.composite_health_score,
          sensor_health_score: data.sensor_health_score,
          ml_anomaly_score: data.ml_anomaly_score,
          health_tier: data.health_tier,
          is_anomaly: data.is_anomaly,
          degradation_reasons: data.degradation_reasons || [],
          penalty_breakdown: data.penalty_breakdown || {
            thermal: 0, vibration: 0, electrical: 0, rpm_slip: 0, ml_anomaly: 0
          }
        });
      }

      // Append to rolling window history (keep max MAX_HISTORY_SAMPLES)
      setTelemetryHistory((prev) => {
        const updated = [...prev, data];
        if (updated.length > MAX_HISTORY_SAMPLES) {
          return updated.slice(updated.length - MAX_HISTORY_SAMPLES);
        }
        return updated;
      });

      // If anomaly detected, log to active alerts list
      if (data.is_anomaly || data.health_tier === 'CRITICAL' || data.health_tier === 'WARNING') {
        const newAlert = {
          motor_id: data.motor_id,
          timestamp: data.timestamp,
          operating_state: data.operating_state,
          composite_health_score: data.composite_health_score,
          ml_anomaly_score: data.ml_anomaly_score,
          reasons: data.degradation_reasons || ['Abnormal telemetry behavior detected'],
          severity: data.health_tier === 'CRITICAL' ? 'CRITICAL' : 'WARNING'
        };
        setAlerts((prevAlerts) => [newAlert, ...prevAlerts.slice(0, 49)]);
      }
    }
  }, [selectedMotor]);

  const { connectionStatus, reconnect } = useWebSocket(handleLiveTelemetry);

  return {
    selectedMotor,
    setSelectedMotor,
    motorList,
    currentTelemetry,
    telemetryHistory,
    healthData,
    alerts,
    modelInfo,
    connectionStatus,
    isLoading,
    refreshData: () => loadInitialData(selectedMotor),
    reconnectWebSocket: reconnect
  };
}
