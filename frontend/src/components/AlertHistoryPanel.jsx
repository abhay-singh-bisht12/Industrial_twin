import React from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle, Info } from 'lucide-react';

export function AlertHistoryPanel({ alerts }) {
  const latestAlert = alerts && alerts.length > 0 ? alerts[0] : null;

  return (
    <div className="industrial-card flex flex-col justify-between">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-rose-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">FAULT ALERT & ANOMALY LOGS</h3>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold">
          {alerts?.length || 0} Events Logged
        </span>
      </div>

      {/* Active Anomaly Banner */}
      {latestAlert ? (
        <div className={`my-3 p-3.5 rounded-lg border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 ${
          latestAlert.severity === 'CRITICAL' 
            ? 'bg-rose-500/10 border-rose-500/40 text-rose-200' 
            : 'bg-amber-500/10 border-amber-500/40 text-amber-200'
        }`}>
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${latestAlert.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'}`}>
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold font-mono uppercase tracking-wider">
                  {latestAlert.severity === 'CRITICAL' ? '🚨 CRITICAL FAULT DETECTED' : '⚠️ ANOMALY ALERT'}
                </span>
                <span className="text-[11px] font-mono opacity-80">&bull; {latestAlert.motor_id}</span>
              </div>
              <p className="text-xs mt-1 font-sans">
                {latestAlert.reasons && latestAlert.reasons.length > 0 ? latestAlert.reasons[0] : `Abnormal ${latestAlert.operating_state} behavior detected`}
              </p>
            </div>
          </div>

          <div className="text-right font-mono shrink-0">
            <div className="text-xs text-slate-400">Health Index</div>
            <div className="text-lg font-bold text-rose-400">
              {latestAlert.composite_health_score ? latestAlert.composite_health_score.toFixed(1) : '--'} %
            </div>
          </div>
        </div>
      ) : (
        <div className="my-3 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>All telemetry streams operating cleanly within normal baseline envelopes.</span>
        </div>
      )}

      {/* Alert History Table */}
      <div className="overflow-x-auto max-h-[220px]">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider sticky top-0 border-b border-slate-800">
            <tr>
              <th className="py-2 px-3">Time</th>
              <th className="py-2 px-3">Motor</th>
              <th className="py-2 px-3">State</th>
              <th className="py-2 px-3">Severity</th>
              <th className="py-2 px-3">Health %</th>
              <th className="py-2 px-3">Description / Reason</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {alerts && alerts.length > 0 ? (
              alerts.slice(0, 10).map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="py-2 px-3 text-slate-400 whitespace-nowrap">
                    {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : '--'}
                  </td>
                  <td className="py-2 px-3 font-bold text-cyan-400">{item.motor_id}</td>
                  <td className="py-2 px-3">{item.operating_state}</td>
                  <td className="py-2 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${
                      item.severity === 'CRITICAL' 
                        ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' 
                        : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                    }`}>
                      {item.severity || 'WARNING'}
                    </span>
                  </td>
                  <td className="py-2 px-3 font-bold">
                    {item.composite_health_score ? item.composite_health_score.toFixed(1) : '--'} %
                  </td>
                  <td className="py-2 px-3 max-w-xs truncate text-slate-400">
                    {item.reasons && item.reasons.length > 0 ? item.reasons[0] : 'Telemetry anomaly'}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="py-4 text-center text-slate-500">
                  No anomaly alerts recorded in history.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}
