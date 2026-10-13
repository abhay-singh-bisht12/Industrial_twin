import React from 'react';
import { Server, Activity, Radio, Clock, ShieldCheck } from 'lucide-react';

export function MotorStatusPanel({ motorId, telemetry, healthData, connectionStatus }) {
  const state = telemetry?.operating_state || 'NORMAL';
  const healthScore = healthData?.composite_health_score ?? 100;
  const temp = telemetry?.temperature ?? 45;
  const vib = telemetry?.vibration_rms ?? 1.2;
  const rpm = telemetry?.rpm ?? 1480;
  const current = telemetry?.current_draw ?? 28.5;
  const voltage = telemetry?.voltage ?? 400;
  const load = telemetry?.load_percentage ?? 75;
  const timestamp = telemetry?.timestamp;

  const getStateColor = () => {
    switch (state) {
      case 'OVERHEATING':
      case 'BEARING_WEAR':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      case 'ELECTRICAL_FAULT':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      default:
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    }
  };

  return (
    <div className="industrial-card flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Server className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">MOTOR STATUS SUMMARY</h3>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-400 font-bold border border-slate-700">
          {motorId}
        </span>
      </div>

      {/* Grid of Attributes */}
      <div className="grid grid-cols-2 gap-3 my-3 text-xs font-mono">
        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
          <span className="text-slate-400 block text-[11px] mb-1">Operating State:</span>
          <span className={`px-2 py-0.5 rounded text-[11px] font-bold border uppercase ${getStateColor()}`}>
            {state}
          </span>
        </div>

        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
          <span className="text-slate-400 block text-[11px] mb-1">Health Score:</span>
          <span className={`text-base font-extrabold ${healthScore >= 80 ? 'text-emerald-400' : healthScore >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
            {healthScore.toFixed(1)} %
          </span>
        </div>

        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
          <span className="text-slate-400 block text-[11px] mb-1">Temperature:</span>
          <span className="text-sm font-bold text-slate-200">{temp.toFixed(1)} °C</span>
        </div>

        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
          <span className="text-slate-400 block text-[11px] mb-1">Vibration RMS:</span>
          <span className="text-sm font-bold text-slate-200">{vib.toFixed(2)} mm/s</span>
        </div>

        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
          <span className="text-slate-400 block text-[11px] mb-1">Shaft Speed:</span>
          <span className="text-sm font-bold text-slate-200">{rpm.toFixed(0)} RPM</span>
        </div>

        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
          <span className="text-slate-400 block text-[11px] mb-1">Current Draw:</span>
          <span className="text-sm font-bold text-slate-200">{current.toFixed(1)} A</span>
        </div>

        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
          <span className="text-slate-400 block text-[11px] mb-1">Line Voltage:</span>
          <span className="text-sm font-bold text-slate-200">{voltage.toFixed(1)} V</span>
        </div>

        <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
          <span className="text-slate-400 block text-[11px] mb-1">Load Ratio:</span>
          <span className="text-sm font-bold text-slate-200">{load.toFixed(0)} %</span>
        </div>
      </div>

      {/* Footer Info */}
      <div className="border-t border-slate-800/80 pt-2 flex items-center justify-between text-xs text-slate-400 font-mono">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span>{timestamp ? new Date(timestamp).toLocaleTimeString() : 'Live Sync'}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Radio className={`w-3.5 h-3.5 ${connectionStatus === 'CONNECTED' ? 'text-emerald-400' : 'text-rose-400'}`} />
          <span>{connectionStatus}</span>
        </div>
      </div>
    </div>
  );
}
