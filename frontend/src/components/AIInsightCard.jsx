import React, { useState } from 'react';
import { Sparkles, Brain, Check, ShieldAlert } from 'lucide-react';
import ConfidenceBadge from './ConfidenceBadge';

export default function AIInsightCard({ suggestion }) {
  const [acknowledged, setAcknowledged] = useState(false);
  const type = suggestion?.anomaly_type || 'General';
  const text = suggestion?.suggestion || '';
  const severity = suggestion?.severity || 'medium';
  const confidence = suggestion?.confidence || 0.85;

  const severityColors = {
    critical: 'border-red-500/30 bg-red-500/5 text-red-400',
    high: 'border-orange-500/30 bg-orange-500/5 text-orange-400',
    medium: 'border-amber-500/30 bg-amber-500/5 text-amber-400',
    low: 'border-cyan-500/30 bg-cyan-500/5 text-cyan-400',
  };

  const border = severityColors[severity] || severityColors.medium;

  return (
    <div className={`glass p-5 rounded-xl border flex flex-col justify-between h-[180px] shrink-0 transition-all ${border} ${acknowledged ? 'opacity-40 scale-[0.99]' : ''}`}>
      {/* Card Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-purple-400" />
          <span className="text-[10px] uppercase font-bold tracking-widest text-purple-300">Suggested Action</span>
        </div>
        <ConfidenceBadge confidence={confidence} />
      </div>

      {/* Suggestion Text */}
      <p className="text-xs font-semibold text-white leading-relaxed my-2 line-clamp-3">
        {text}
      </p>

      {/* Card Actions Footer */}
      <div className="flex items-center justify-between border-t border-white/5 pt-2 mt-1">
        <span className="text-[9px] uppercase font-bold tracking-wider opacity-60 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-cyan-400" />
          <span>Context: {type.replace('_', ' ')}</span>
        </span>

        <button
          onClick={() => setAcknowledged(!acknowledged)}
          className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-[10px] font-bold tracking-wider uppercase transition-all ${
            acknowledged 
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'bg-white/10 hover:bg-white/15 text-white active:scale-95 border border-white/5'
          }`}
        >
          {acknowledged ? (
            <>
              <Check className="w-3.5 h-3.5" />
              <span>Acknowledged</span>
            </>
          ) : (
            <span>Mark Actioned</span>
          )}
        </button>
      </div>
    </div>
  );
}
