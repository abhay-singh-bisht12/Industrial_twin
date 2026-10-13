import React from 'react';

export function TelemetryCard({
  title,
  value,
  unit,
  icon: Icon,
  status = 'NORMAL', // NORMAL, WARNING, CRITICAL
  lastUpdated,
  description
}) {
  const getStatusColor = () => {
    switch (status) {
      case 'CRITICAL':
        return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
      case 'WARNING':
        return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
      default:
        return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    }
  };

  const getIconColor = () => {
    switch (status) {
      case 'CRITICAL':
        return 'text-rose-400 bg-rose-500/20';
      case 'WARNING':
        return 'text-amber-400 bg-amber-500/20';
      default:
        return 'text-cyan-400 bg-cyan-500/20';
    }
  };

  return (
    <div className="industrial-card flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`p-1.5 rounded-lg ${getIconColor()}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="my-2 flex items-baseline justify-between">
        <div className="flex items-baseline gap-1">
          <span className="text-2xl font-extrabold text-white font-mono tracking-tight">
            {typeof value === 'number' ? value.toFixed(1) : value ?? '--'}
          </span>
          <span className="text-xs font-bold text-slate-400 font-sans">{unit}</span>
        </div>
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${getStatusColor()}`}>
          {status}
        </span>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-800/80 pt-2 font-mono">
        <span>{description || 'Realtime Sensor'}</span>
        <span>{lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : 'Live'}</span>
      </div>
    </div>
  );
}
