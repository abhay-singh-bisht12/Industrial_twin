import React, { useState } from 'react';
import { Sliders, Send, RotateCcw, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';
import { api } from '../services/api';

export function FaultControlPanel({ selectedMotor, onCommandExecuted }) {
  const [targetState, setTargetState] = useState('NORMAL');
  const [loadPct, setLoadPct] = useState(75);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [commandFeedback, setCommandFeedback] = useState(null); // { type: 'success'|'error', text: '' }

  const handleApplyControl = async (stateToApply, loadToApply) => {
    setIsSubmitting(true);
    setCommandFeedback({ type: 'info', text: 'Transmitting control payload to MQTT broker...' });

    try {
      const res = await api.controlMotor(selectedMotor, stateToApply, loadToApply);
      if (res && res.status === 'published') {
        setCommandFeedback({
          type: 'success',
          text: `Command Accepted: Motor ${selectedMotor} set to ${stateToApply} at ${loadToApply}% load.`
        });
        if (onCommandExecuted) onCommandExecuted();
      } else {
        setCommandFeedback({
          type: 'error',
          text: `Command Failed: ${res?.detail || 'MQTT broker returned an unexpected status.'}`
        });
      }
    } catch (err) {
      setCommandFeedback({
        type: 'error',
        text: `Command Failed: ${err.message || 'Network error sending control payload'}`
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setTargetState('NORMAL');
    setLoadPct(75);
    handleApplyControl('NORMAL', 75);
  };

  return (
    <div className="industrial-card flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">FAULT INJECTION CONTROL PANEL</h3>
        </div>
        <span className="text-xs font-mono text-slate-400">Target: {selectedMotor}</span>
      </div>

      <div className="space-y-4 my-3">
        {/* Operating State Selector Buttons */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Operating State Injection:
          </label>
          <div className="grid grid-cols-2 gap-2 text-xs font-bold font-mono">
            <button
              onClick={() => setTargetState('NORMAL')}
              className={`p-2.5 rounded border transition flex items-center justify-center gap-1.5 ${
                targetState === 'NORMAL'
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-md'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              <span>✅ NORMAL</span>
            </button>
            <button
              onClick={() => setTargetState('OVERHEATING')}
              className={`p-2.5 rounded border transition flex items-center justify-center gap-1.5 ${
                targetState === 'OVERHEATING'
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-md'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              <span>🔥 OVERHEATING</span>
            </button>
            <button
              onClick={() => setTargetState('BEARING_WEAR')}
              className={`p-2.5 rounded border transition flex items-center justify-center gap-1.5 ${
                targetState === 'BEARING_WEAR'
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-md'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              <span>⚙️ BEARING WEAR</span>
            </button>
            <button
              onClick={() => setTargetState('ELECTRICAL_FAULT')}
              className={`p-2.5 rounded border transition flex items-center justify-center gap-1.5 ${
                targetState === 'ELECTRICAL_FAULT'
                  ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 shadow-md'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              <span>⚡ ELEC FAULT</span>
            </button>
          </div>
        </div>

        {/* Load Percentage Slider */}
        <div>
          <div className="flex justify-between items-center text-xs mb-1 font-mono">
            <span className="text-slate-400 font-semibold uppercase tracking-wider">Mechanical Load Ratio:</span>
            <span className="text-cyan-400 font-bold">{loadPct} %</span>
          </div>
          <input
            type="range"
            min="0"
            max="125"
            value={loadPct}
            onChange={(e) => setLoadPct(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-400 border border-slate-800"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
            <span>0% (Idle)</span>
            <span>75% (Nominal)</span>
            <span>125% (Overload)</span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 pt-2 border-t border-slate-800/80">
        <button
          onClick={() => handleApplyControl(targetState, loadPct)}
          disabled={isSubmitting}
          className="flex-1 py-2.5 px-4 rounded-lg bg-cyan-600 hover:bg-cyan-500 active:bg-cyan-700 disabled:opacity-50 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg transition"
        >
          {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          <span>TRANSMIT CONTROL STATE</span>
        </button>

        <button
          onClick={handleReset}
          disabled={isSubmitting}
          className="py-2.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-semibold flex items-center justify-center gap-1.5 transition"
        >
          <RotateCcw className="w-4 h-4" />
          <span>RESET</span>
        </button>
      </div>

      {/* Feedback Banner */}
      {commandFeedback && (
        <div
          className={`mt-3 p-2.5 rounded-lg text-xs font-mono flex items-center gap-2 border ${
            commandFeedback.type === 'success'
              ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
              : commandFeedback.type === 'error'
              ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
              : 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30'
          }`}
        >
          {commandFeedback.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : commandFeedback.type === 'error' ? (
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          ) : (
            <Loader2 className="w-4 h-4 text-cyan-400 animate-spin shrink-0" />
          )}
          <span>{commandFeedback.text}</span>
        </div>
      )}
    </div>
  );
}
