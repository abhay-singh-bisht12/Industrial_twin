import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

export function TelemetryCharts({ telemetryHistory }) {
  const [activeTab, setActiveTab] = useState('temp'); // temp, vib, rpm, current, health

  // Format history data for Recharts
  const chartData = (telemetryHistory || []).map((item) => {
    const timeStr = item.timestamp
      ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      : '';
    return {
      time: timeStr,
      temp: item.temperature ?? 0,
      vib: item.vibration_rms ?? 0,
      vibPeak: item.vibration_peak ?? 0,
      rpm: item.rpm ?? 0,
      current: item.current_draw ?? 0,
      voltage: item.voltage ?? 0,
      health: item.composite_health_score ?? 100
    };
  });

  const renderActiveChart = () => {
    switch (activeTab) {
      case 'vib':
        return (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 15]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="vib" name="Vibration RMS (mm/s)" stroke="#f59e0b" strokeWidth={2} dot={false} isAnimationActive={false} />
              <Line type="monotone" dataKey="vibPeak" name="Vibration Peak (g)" stroke="#ef4444" strokeWidth={1.5} strokeDasharray="3 3" dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'rpm':
        return (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[1200, 1600]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="rpm" name="Speed (RPM)" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'current':
        return (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 70]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="current" name="Current (A)" stroke="#38bdf8" strokeWidth={2} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'health':
        return (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="health" name="Health Score (%)" stroke="#a855f7" strokeWidth={2.5} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        );
      default: // Temperature
        return (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[30, 110]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="temp" name="Temperature (°C)" stroke="#ef4444" strokeWidth={2} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        );
    }
  };

  return (
    <div className="industrial-card flex flex-col justify-between">
      {/* Header & Metric Selector Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-3">
        <div>
          <h3 className="text-sm font-bold text-white tracking-wide">LIVE TELEMETRY TIME-SERIES</h3>
          <p className="text-xs text-slate-400 font-mono">Rolling window history buffer (Last 80 samples)</p>
        </div>

        <div className="flex flex-wrap items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('temp')}
            className={`px-2.5 py-1 rounded transition ${activeTab === 'temp' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            Temp
          </button>
          <button
            onClick={() => setActiveTab('vib')}
            className={`px-2.5 py-1 rounded transition ${activeTab === 'vib' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            Vibration
          </button>
          <button
            onClick={() => setActiveTab('rpm')}
            className={`px-2.5 py-1 rounded transition ${activeTab === 'rpm' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            RPM
          </button>
          <button
            onClick={() => setActiveTab('current')}
            className={`px-2.5 py-1 rounded transition ${activeTab === 'current' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            Current
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`px-2.5 py-1 rounded transition ${activeTab === 'health' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
          >
            Health
          </button>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="pt-4">
        {chartData.length > 0 ? (
          renderActiveChart()
        ) : (
          <div className="h-[260px] flex items-center justify-center text-slate-500 text-xs font-mono">
            Waiting for live telemetry stream...
          </div>
        )}
      </div>
    </div>
  );
}
