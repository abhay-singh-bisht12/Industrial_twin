const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function handleResponse(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  async getMotorList() {
    const res = await fetch(`${API_BASE_URL}/telemetry/motors`);
    return handleResponse(res);
  },

  async getMotorStatus(motorId = 'motor-01') {
    const res = await fetch(`${API_BASE_URL}/telemetry/status?motor_id=${encodeURIComponent(motorId)}`);
    return handleResponse(res);
  },

  async getRecentTelemetry(motorId = 'motor-01', limit = 50) {
    const res = await fetch(`${API_BASE_URL}/telemetry/recent?motor_id=${encodeURIComponent(motorId)}&limit=${limit}`);
    return handleResponse(res);
  },

  async getTelemetryStats(motorId = 'motor-01', minutes = 60) {
    const res = await fetch(`${API_BASE_URL}/telemetry/stats?motor_id=${encodeURIComponent(motorId)}&minutes=${minutes}`);
    return handleResponse(res);
  },

  async getMachineHealth(motorId = 'motor-01') {
    const res = await fetch(`${API_BASE_URL}/ml/health?motor_id=${encodeURIComponent(motorId)}`);
    return handleResponse(res);
  },

  async getHealthHistory(motorId = 'motor-01', limit = 50) {
    const res = await fetch(`${API_BASE_URL}/ml/health/history?motor_id=${encodeURIComponent(motorId)}&limit=${limit}`);
    return handleResponse(res);
  },

  async getAnomalies(motorId = null, limit = 50) {
    const url = motorId 
      ? `${API_BASE_URL}/ml/anomalies?motor_id=${encodeURIComponent(motorId)}&limit=${limit}`
      : `${API_BASE_URL}/ml/anomalies?limit=${limit}`;
    const res = await fetch(url);
    return handleResponse(res);
  },

  async getModelInfo() {
    const res = await fetch(`${API_BASE_URL}/ml/model-info`);
    return handleResponse(res);
  },

  async controlMotor(motorId, state, loadPercentage) {
    const body = { motor_id: motorId };
    if (state) body.state = state;
    if (loadPercentage !== undefined && loadPercentage !== null) body.load_percentage = parseFloat(loadPercentage);

    const res = await fetch(`${API_BASE_URL}/telemetry/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    return handleResponse(res);
  }
};
