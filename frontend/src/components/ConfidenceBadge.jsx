import React from 'react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

export default function ConfidenceBadge({ confidence }) {
  const pct = Math.round(confidence * 100);
  
  let color = 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400';
  let Icon = ShieldCheck;
  
  if (confidence < 0.60) {
    color = 'bg-red-500/10 border-red-500/20 text-red-400';
    Icon = ShieldAlert;
  } else if (confidence < 0.80) {
    color = 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400';
    Icon = ShieldCheck;
  }

  return (
    <div className={`flex items-center gap-1 px-2 py-0.5 rounded border text-[10px] font-semibold tracking-wide ${color}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{pct}% AI Confidence</span>
    </div>
  );
}
