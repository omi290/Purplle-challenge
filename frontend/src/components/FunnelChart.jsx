import React from 'react';
import { ArrowDown, HelpCircle } from 'lucide-react';

export default function FunnelChart({ funnelData }) {
  const stages = funnelData?.stages || [];

  return (
    <div className="glass p-6 rounded-xl border border-gray-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Store Conversion Funnel</h3>
          <span className="text-[10px] text-gray-500 font-medium">Customer journey progression & friction thresholds</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-lg text-xs font-semibold text-purple-400">
          <HelpCircle className="w-4 h-4" />
          <span>Goal Target: 35.0%</span>
        </div>
      </div>

      {/* Tapered Funnel Stage Bars */}
      <div className="space-y-4 max-w-2xl mx-auto py-4">
        {stages.map((stage, idx) => {
          // Adjust width tapering for the classic funnel visual look
          const widths = ['w-full', 'w-[85%]', 'w-[70%]', 'w-[55%]'];
          const colors = [
            'from-purple-600/40 to-purple-600/10 border-purple-500/30',
            'from-cyan-600/40 to-cyan-600/10 border-cyan-500/30',
            'from-amber-600/40 to-amber-600/10 border-amber-500/30',
            'from-emerald-600/40 to-emerald-600/10 border-emerald-500/30'
          ];
          
          const textGlows = ['glow-purple', 'glow-cyan', 'text-amber-400', 'text-emerald-400'];

          return (
            <div key={stage.name} className="flex flex-col items-center">
              {/* Funnel Stage Bar */}
              <div className={`flex items-center justify-between px-6 py-3.5 bg-gradient-to-r ${colors[idx]} border rounded-xl shadow-glass ${widths[idx]} transition-all duration-500`}>
                <div className="flex items-center gap-3">
                  <span className="text-xs font-bold text-gray-400">0{idx+1}</span>
                  <span className="text-sm font-semibold text-white">{stage.name}</span>
                </div>
                
                <div className="flex items-center gap-6">
                  <span className="text-xs font-medium text-gray-400">{stage.count} visitors</span>
                  <span className={`text-sm font-black ${textGlows[idx]}`}>{stage.percentage}%</span>
                </div>
              </div>

              {/* Drop-off Indicator between stages */}
              {idx < stages.length - 1 && (
                <div className="flex flex-col items-center my-1">
                  <div className="w-0.5 h-6 bg-gradient-to-b from-gray-700 to-gray-800"></div>
                  <div className="flex items-center gap-1.5 px-2.5 py-0.5 bg-red-500/10 border border-red-500/20 rounded-full text-[9px] font-bold text-red-400">
                    <ArrowDown className="w-3 h-3" />
                    <span>-{stages[idx+1].drop_off}% drop-off</span>
                  </div>
                  <div className="w-0.5 h-6 bg-gradient-to-b from-gray-800 to-gray-700"></div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
