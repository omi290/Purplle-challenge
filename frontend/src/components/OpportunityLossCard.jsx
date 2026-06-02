import React from 'react';
import { IndianRupee, Award, ShieldAlert, Percent, Clock } from 'lucide-react';

export default function OpportunityLossCard({ opportunityData }) {
  const score = opportunityData?.opportunity_score !== undefined ? opportunityData.opportunity_score : 100;
  const oppVal = opportunityData?.estimated_revenue_opportunity || 0;
  const contrib = opportunityData?.contributors || {};

  return (
    <div className="glass p-6 rounded-xl border border-gray-800 flex flex-col justify-between h-[450px]">
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Opportunity Loss Tracker</h3>
            <span className="text-[10px] text-gray-500 font-medium">Floor conversion & layout leakage</span>
          </div>
          {/* Opportunity score badge */}
          <div className="px-2.5 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-right">
            <span className="text-[8px] uppercase font-bold text-cyan-400 tracking-widest block leading-none">Score</span>
            <span className="text-sm font-black text-white block mt-0.5 leading-none">{score}/100</span>
          </div>
        </div>
      </div>

      {/* Main Opportunity Value Pool */}
      <div className="my-3 bg-cyan-500/5 border border-cyan-500/10 p-4 rounded-xl text-center shadow-[0_0_15px_rgba(6,182,212,0.05)]">
        <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">Estimated Revenue Opportunity</span>
        <div className="flex items-center justify-center text-3xl font-black text-white mt-1">
          <IndianRupee className="w-6 h-6 text-cyan-400 mr-0.5" />
          <span>{oppVal.toLocaleString('en-IN')}</span>
        </div>
        <p className="text-[8px] text-gray-500 mt-1.5 max-w-[200px] mx-auto leading-relaxed">
          Realistic target of converting 15% of missed/unconverted floor traffic today.
        </p>
      </div>

      {/* Contributors breakdown with progress meters */}
      <div className="space-y-2.5 border-t border-gray-800/60 pt-3">
        <span className="text-[10px] uppercase tracking-wider font-bold text-gray-500 block">Conversion Leakage Contributors</span>
        
        {/* Queue Abandonment */}
        <div className="space-y-1">
          <div className="flex justify-between text-[10px] font-semibold text-gray-300">
            <span className="flex items-center gap-1"><ShieldAlert className="w-3.5 h-3.5 text-rose-500" />Queue Abandonment</span>
            <span className="text-gray-400 font-normal">-{contrib.queue_abandonment || 0} pts</span>
          </div>
          <div className="h-1 bg-gray-900 rounded-full overflow-hidden">
            <div 
              className="h-full bg-rose-500 transition-all duration-1000" 
              style={{ width: `${((contrib.queue_abandonment || 0) / 30) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Dead Zones */}
        <div className="space-y-1">
          <div className="flex justify-between text-[10px] font-semibold text-gray-300">
            <span className="flex items-center gap-1"><Award className="w-3.5 h-3.5 text-amber-500" />Active Dead Zones</span>
            <span className="text-gray-400 font-normal">-{contrib.dead_zones || 0} pts</span>
          </div>
          <div className="h-1 bg-gray-900 rounded-full overflow-hidden">
            <div 
              className="h-full bg-amber-500 transition-all duration-1000" 
              style={{ width: `${((contrib.dead_zones || 0) / 30) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Low Conversion Zones */}
        <div className="space-y-1">
          <div className="flex justify-between text-[10px] font-semibold text-gray-300">
            <span className="flex items-center gap-1"><Percent className="w-3.5 h-3.5 text-purple-500" />Low Conversion Zones</span>
            <span className="text-gray-400 font-normal">-{contrib.low_conversion_zones || 0} pts</span>
          </div>
          <div className="h-1 bg-gray-900 rounded-full overflow-hidden">
            <div 
              className="h-full bg-purple-500 transition-all duration-1000" 
              style={{ width: `${((contrib.low_conversion_zones || 0) / 20) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Low Dwell Zones */}
        <div className="space-y-1">
          <div className="flex justify-between text-[10px] font-semibold text-gray-300">
            <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-cyan-500" />Low Dwell browse zones</span>
            <span className="text-gray-400 font-normal">-{contrib.low_dwell_zones || 0} pts</span>
          </div>
          <div className="h-1 bg-gray-900 rounded-full overflow-hidden">
            <div 
              className="h-full bg-cyan-500 transition-all duration-1000" 
              style={{ width: `${((contrib.low_dwell_zones || 0) / 20) * 100}%` }}
            ></div>
          </div>
        </div>

      </div>
    </div>
  );
}
