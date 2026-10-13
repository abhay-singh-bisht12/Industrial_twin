import React from 'react';
import { ShieldCheck, AlertTriangle, AlertCircle, Cpu } from 'lucide-react';

export function HealthScoreCard({ healthData }) {
  const compositeScore = healthData?.composite_health_score ?? 100.0;
  const sensorScore = healthData?.sensor_health_score ?? 100.0;
  const mlAnomalyScore = healthData?.ml_anomaly_score ?? 0.0;
  const healthTier = healthData?.health_tier || 'HEALTHY';
  const isAnomaly = healthData?.is_anomaly || false;
  const reasons = healthData?.degradation_reasons || ['Operating normally'];
  const breakdown = healthData?.penalty_breakdown || {
    thermal: 0, vibration: 0, electrical: 0, rpm_slip: 0, ml_anomaly: 0
  };

  const getTierColor = () => {
    switch (healthTier) {
      case 'CRITICAL':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      case 'WARNING':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      default:
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    }
  };

  const getProgressColor = () => {
    if (compositeScore >= 80) return 'bg-emerald-500';
    if (compositeScore >= 50) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className="industrial-card flex flex-col justify-between">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">MACHINE HEALTH INDEX</h3>
        </div>
        <div className={`px-2.5 py-1 rounded text-xs font-bold border uppercase tracking-wider ${getTierColor()}`}>
          {healthTier}
        </div>
      </div>

      {/* Primary Health Score Gauge */}
      <div className="py-4 my-2 flex items-center justify-between gap-6">
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-5xl font-extrabold tracking-tight text-white font-mono">
              {compositeScore.toFixed(1)}
            </span>
            <span className="text-lg font-bold text-slate-400">/ 100</span>
          </div>
          <div className="mt-2 flex items-center gap-2 text-xs">
            <span className="text-slate-400">Status:</span>
            {isAnomaly ? (
              <span className="inline-flex items-center gap-1 font-bold text-rose-400">
                <AlertTriangle className="w-3.5 h-3.5" /> ANOMALY DETECTED
              </span>
            ) : (
              <span className="font-bold text-emerald-400">NORMAL BEHAVIOR</span>
            )}
          </div>
        </div>

        {/* Circular Progress Indicator */}
        <div className="w-24 h-24 relative flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
            <path
              className="text-slate-800"
              strokeWidth="3.5"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              className={compositeScore >= 80 ? 'text-emerald-500' : compositeScore >= 50 ? 'text-amber-500' : 'text-rose-500'}
              strokeDasharray={`${compositeScore}, 100`}
              strokeWidth="3.5"
              strokeLinecap="round"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <Cpu className="w-8 h-8 text-cyan-400 absolute" />
        </div>
      </div>

      {/* Sub-Scores & ML Breakdown */}
      <div className="grid grid-cols-2 gap-2 py-2 border-t border-b border-slate-800/80 text-xs font-mono">
        <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
          <span className="text-slate-400 block text-[11px]">Sensor Score:</span>
          <span className="text-sm font-bold text-slate-200">{sensorScore.toFixed(1)} %</span>
        </div>
        <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
          <span className="text-slate-400 block text-[11px]">ML Anomaly Score:</span>
          <span className={`text-sm font-bold ${mlAnomalyScore > 0.65 ? 'text-rose-400' : 'text-cyan-400'}`}>
            {mlAnomalyScore.toFixed(4)}
          </span>
        </div>
      </div>

      {/* Penalty Breakdown */}
      <div className="mt-3 text-xs space-y-1.5 font-mono">
        <div className="text-[11px] font-sans font-semibold text-slate-400 uppercase tracking-wider mb-1">
          Deductions & Penalties:
        </div>
        <div className="flex justify-between items-center text-slate-300">
          <span>Thermal Deduction:</span>
          <span className={breakdown.thermal > 0 ? 'text-rose-400 font-bold' : 'text-slate-500'}>
            -{breakdown.thermal.toFixed(1)} pts
          </span>
        </div>
        <div className="flex justify-between items-center text-slate-300">
          <span>Vibration Deduction:</span>
          <span className={breakdown.vibration > 0 ? 'text-amber-400 font-bold' : 'text-slate-500'}>
            -{breakdown.vibration.toFixed(1)} pts
          </span>
        </div>
        <div className="flex justify-between items-center text-slate-300">
          <span>Electrical Deduction:</span>
          <span className={breakdown.electrical > 0 ? 'text-rose-400 font-bold' : 'text-slate-500'}>
            -{breakdown.electrical.toFixed(1)} pts
          </span>
        </div>
        <div className="flex justify-between items-center text-slate-300">
          <span>ML Anomaly Deduction:</span>
          <span className={breakdown.ml_anomaly > 0 ? 'text-rose-400 font-bold' : 'text-slate-500'}>
            -{breakdown.ml_anomaly.toFixed(1)} pts
          </span>
        </div>
      </div>

      {/* Degradation Reasons */}
      <div className="mt-3 pt-2 border-t border-slate-800/80">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
          Primary Failure Risks / Reasons:
        </div>
        <ul className="space-y-1 text-xs text-slate-300 font-sans">
          {reasons.slice(0, 2).map((reason, idx) => (
            <li key={idx} className="flex items-start gap-1.5 text-slate-300">
              <AlertCircle className="w-3.5 h-3.5 text-amber-400 mt-0.5 shrink-0" />
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </div>

    </div>
  );
}
