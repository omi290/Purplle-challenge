import React from 'react';
import { IndianRupee, TrendingDown, ArrowRightCircle } from 'lucide-react';

export default function OpportunityLossCard({ opportunityData }) {
  const lostCount = opportunityData?.total_opportunities_lost || 0;
  const lostVal = opportunityData?.estimated_revenue_impact || 0;
  const reasons = opportunityData?.top_reasons || [];

  return (
    <div className="glass p-6 rounded-xl border border-gray-800 flex flex-col justify-between h-[450px]">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Opportunity Loss Tracker</h3>
        <span className="text-[10px] text-gray-500 font-medium">Missed visitor conversions index</span>
      </div>

      {/* Main lost value representation */}
      <div className="my-4 bg-red-500/5 border border-red-500/10 p-5 rounded-xl text-center">
        <span className="text-[10px] uppercase font-bold text-red-400 tracking-wider">Estimated Missed Sales Pool</span>
        <div className="flex items-center justify-center text-3xl font-black text-white mt-1">
          <IndianRupee className="w-6 h-6 text-red-500 mr-1" />
          <span>{lostVal.toLocaleString('en-IN')}</span>
        </div>
        <div className="flex items-center justify-center gap-1.5 mt-2 text-xs font-semibold text-gray-400">
          <TrendingDown className="w-4 h-4 text-red-500" />
          <span>{lostCount} unconverted visitors</span>
        </div>
      </div>

      {/* Reasons breakdown list */}
      <div className="space-y-3 border-t border-gray-800/60 pt-4">
        <span className="text-[10px] uppercase tracking-wider font-bold text-gray-500 block">Critical Conversion Obstacles</span>
        {reasons.slice(0, 3).map((reason, idx) => (
          <div key={idx} className="flex gap-2 text-xs">
            <ArrowRightCircle className="w-4 h-4 text-red-500/70 shrink-0 mt-0.5" />
            <span className="text-gray-300 leading-relaxed">{reason}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
