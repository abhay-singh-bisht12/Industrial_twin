import React from 'react';
import { useMotorData } from './hooks/useMotorData';
import { Header } from './components/Header';
import { MotorDigitalTwin3D } from './components/MotorDigitalTwin3D';
import { HealthScoreCard } from './components/HealthScoreCard';
import { TelemetryCard } from './components/TelemetryCard';
import { TelemetryCharts } from './components/TelemetryCharts';
import { MotorStatusPanel } from './components/MotorStatusPanel';
import { FaultControlPanel } from './components/FaultControlPanel';
import { AlertHistoryPanel } from './components/AlertHistoryPanel';

import {
  Thermometer,
  Activity,
  Gauge,
  Zap,
  Percent,
  Sliders
} from 'lucide-react';

export default function App() {
  const {
    selectedMotor,
    setSelectedMotor,
    motorList,
    currentTelemetry,
    telemetryHistory,
    healthData,
    alerts,
    connectionStatus,
    refreshData
  } = useMotorData('motor-01');

  // Compute status helpers for cards
  const getTempStatus = (t) => {
    if (!t) return 'NORMAL';
    if (t > 85) return 'CRITICAL';
    if (t > 65) return 'WARNING';
    return 'NORMAL';
  };

  const getVibStatus = (v) => {
    if (!v) return 'NORMAL';
    if (v > 4.5) return 'CRITICAL';
    if (v > 2.8) return 'WARNING';
    return 'NORMAL';
  };

  const getCurrentStatus = (i) => {
    if (!i) return 'NORMAL';
    if (i > 45) return 'CRITICAL';
    if (i > 35) return 'WARNING';
    return 'NORMAL';
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans">
      
      {/* 1. Header Navigation Bar */}
      <Header
        selectedMotor={selectedMotor}
        setSelectedMotor={setSelectedMotor}
        motorList={motorList}
        connectionStatus={connectionStatus}
        onRefresh={refreshData}
      />

      {/* Main Dashboard Layout Area */}
      <main className="flex-1 p-4 md:p-6 space-y-6 max-w-[1800px] w-full mx-auto">

        {/* Section 1: Top Main Row (3D Digital Twin + Machine Health Index) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7">
            <MotorDigitalTwin3D telemetry={currentTelemetry} healthData={healthData} />
          </div>
          <div className="lg:col-span-5 flex flex-col">
            <HealthScoreCard healthData={healthData} />
          </div>
        </div>

        {/* Section 2: Real-time Telemetry Sensor Cards Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
          <TelemetryCard
            title="Temperature"
            value={currentTelemetry?.temperature}
            unit="°C"
            icon={Thermometer}
            status={getTempStatus(currentTelemetry?.temperature)}
            lastUpdated={currentTelemetry?.timestamp}
            description="Stator Thermal Sensor"
          />
          <TelemetryCard
            title="Vibration RMS"
            value={currentTelemetry?.vibration_rms}
            unit="mm/s"
            icon={Activity}
            status={getVibStatus(currentTelemetry?.vibration_rms)}
            lastUpdated={currentTelemetry?.timestamp}
            description="Bearing Velocity RMS"
          />
          <TelemetryCard
            title="Vibration Peak"
            value={currentTelemetry?.vibration_peak}
            unit="g"
            icon={Activity}
            status={getVibStatus(currentTelemetry?.vibration_peak)}
            lastUpdated={currentTelemetry?.timestamp}
            description="Impact Peak Acceleration"
          />
          <TelemetryCard
            title="Shaft Speed"
            value={currentTelemetry?.rpm}
            unit="RPM"
            icon={Gauge}
            status="NORMAL"
            lastUpdated={currentTelemetry?.timestamp}
            description="Optical Encoder Speed"
          />
          <TelemetryCard
            title="Phase Current"
            value={currentTelemetry?.current_draw}
            unit="A"
            icon={Zap}
            status={getCurrentStatus(currentTelemetry?.current_draw)}
            lastUpdated={currentTelemetry?.timestamp}
            description="Current Sensor Transducer"
          />
          <TelemetryCard
            title="Mechanical Load"
            value={currentTelemetry?.load_percentage}
            unit="%"
            icon={Percent}
            status="NORMAL"
            lastUpdated={currentTelemetry?.timestamp}
            description="Shaft Load Ratio"
          />
        </div>

        {/* Section 3: Middle Row (Time-Series Charts + Status & Control Panels) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Time-Series Charts */}
          <div className="lg:col-span-7">
            <TelemetryCharts telemetryHistory={telemetryHistory} />
          </div>

          {/* Motor Status & Control Panel */}
          <div className="lg:col-span-5 space-y-6 flex flex-col justify-between">
            <MotorStatusPanel
              motorId={selectedMotor}
              telemetry={currentTelemetry}
              healthData={healthData}
              connectionStatus={connectionStatus}
            />
            <FaultControlPanel
              selectedMotor={selectedMotor}
              onCommandExecuted={refreshData}
            />
          </div>
        </div>

        {/* Section 4: Fault Alert System & Log History Table */}
        <div>
          <AlertHistoryPanel alerts={alerts} />
        </div>

      </main>

      {/* Footer */}
      <footer className="bg-[#0b0f19] border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500 font-mono">
        IndustrialTwin Platform &bull; Real-time Industrial Equipment Health Monitoring &bull; React + Three.js + FastAPI + MQTT + MongoDB
      </footer>

    </div>
  );
}
