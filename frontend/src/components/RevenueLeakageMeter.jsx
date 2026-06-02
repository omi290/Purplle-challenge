import React from 'react';
import { IndianRupee, AlertTriangle, Coins } from 'lucide-react';

export default function RevenueLeakageMeter({ leakageData }) {
  const rate = leakageData?.leakage_rate || 0;
  const leakedVal = leakageData?.estimated_leaked_revenue || 0;
  const potentialVal = leakageData?.potential_total_revenue || 0;
  const actualVal = leakageData?.actual_sales || 0;

  const pct = Math.round(rate * 1000) / 10;

  return (
    <div className="glass p-6 rounded-xl border border-gray-800 flex flex-col justify-between h-[450px]">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Revenue Leakage Meter</h3>
        <span className="text-[10px] text-gray-500 font-medium">Checkout drop-off & queue leakage index</span>
      </div>

      {/* Visual Vertical Bar Meter */}
      <div className="flex items-center justify-between gap-6 my-4 h-48">
        {/* Actual vs Lost Bars */}
        <div className="flex-1 flex flex-col gap-4">
          {/* Actual Sales */}
          <div>
            <span className="text-[10px] uppercase font-bold text-gray-500">Converted Sales</span>
            <div className="flex items-center text-xl font-bold text-emerald-400 mt-0.5">
              <IndianRupee className="w-4 h-4" />
              <span>{actualVal.toLocaleString('en-IN')}</span>
            </div>
          </div>

          {/* Leaked Revenue */}
          <div>
            <div className="flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5 text-red-500" />
              <span className="text-[10px] uppercase font-bold text-gray-500">Leaked Revenue</span>
            </div>
            <div className="flex items-center text-xl font-bold text-red-400 mt-0.5">
              <IndianRupee className="w-4 h-4" />
              <span>{leakedVal.toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>

        {/* Leaked rate visual meter bar */}
        <div className="w-16 h-full bg-gray-900 border border-gray-800 rounded-xl relative overflow-hidden flex flex-col justify-end p-1">
          <div 
            className="w-full bg-gradient-to-t from-red-600 via-orange-500 to-amber-400 rounded-lg transition-all duration-1000"
            style={{ height: `${Math.max(8, Math.min(100, rate * 300))}%` }}
          >
            {/* Value floating inside bar */}
            <div className="absolute inset-0 flex items-center justify-center font-black text-xs text-white uppercase tracking-widest rotate-90">
              {pct}% Leaked
            </div>
          </div>
        </div>
      </div>

      {/* Potential Earnings Summary */}
      <div className="border-t border-gray-800/60 pt-4 mt-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400 font-medium flex items-center gap-1">
            <Coins className="w-4 h-4 text-cyan-400" />
            <span>Potential Revenue Pool</span>
          </span>
          <span className="font-extrabold text-white text-sm flex items-center">
            <IndianRupee className="w-3.5 h-3.5" />
            <span>{potentialVal.toLocaleString('en-IN')}</span>
          </span>
        </div>
        <p className="text-[10px] text-gray-500 mt-2 leading-relaxed">
          Leakage indicates visitors who joined the checkout queue area but left without a correlating POS transaction occurring.
        </p>
      </div>
    </div>
  );
}
