import React, { useState, useEffect } from 'react';
import { Activity, Radio, ExternalLink, Cpu, RefreshCw } from 'lucide-react';

export function Header({
  selectedMotor,
  setSelectedMotor,
  motorList,
  connectionStatus,
  onRefresh
}) {
  const [utcTime, setUtcTime] = useState(new Date().toUTCString());

  useEffect(() => {
    const timer = setInterval(() => {
      setUtcTime(new Date().toUTCString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const getStatusBadge = () => {
    switch (connectionStatus) {
      case 'CONNECTED':
        return (
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            MQTT / Backend Connected
          </span>
        );
      case 'RECONNECTING':
      case 'CONNECTING':
        return (
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
            Reconnecting Backend...
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
            Backend Disconnected
          </span>
        );
    }
  };

  return (
    <header className="bg-[#111827] border-b border-slate-800 px-6 py-4 shadow-2xl">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        
        {/* Left: Brand Title */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">IndustrialTwin</h1>
              <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono border border-cyan-500/30">v1.0.0</span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Digital Twin &bull; Real-time Industrial Equipment Health Monitoring
            </p>
          </div>
        </div>

        {/* Center/Right Controls */}
        <div className="flex flex-wrap items-center gap-3">
          
          {/* Motor Selector Dropdown */}
          <div className="flex items-center gap-2 bg-[#1e293b] border border-slate-700/80 rounded-lg px-3 py-1.5">
            <span className="text-xs text-slate-400 font-medium">Motor:</span>
            <select
              value={selectedMotor}
              onChange={(e) => setSelectedMotor(e.target.value)}
              className="bg-transparent text-sm font-semibold text-cyan-300 focus:outline-none cursor-pointer"
            >
              {motorList.map((m) => (
                <option key={m} value={m} className="bg-[#1e293b] text-white">
                  {m}
                </option>
              ))}
            </select>
          </div>

          {/* Connection Status Indicator */}
          {getStatusBadge()}

          {/* UTC Clock */}
          <div className="hidden xl:flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            <span>{utcTime}</span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            title="Refresh API Data"
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          {/* External Grafana Button */}
          <a
            href="http://localhost:3001"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-400 border border-amber-500/30 transition shadow-sm"
          >
            <span>Open Grafana</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

        </div>
      </div>
    </header>
  );
}
