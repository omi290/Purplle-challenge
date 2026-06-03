import React from 'react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import ConfidenceBadge from './ConfidenceBadge';

export default function MetricCard({ title, value, change, icon: Icon, color, trendData, confidence }) {
  const isPositive = change >= 0;
  
  const colors = {
    purple: {
      text: 'text-purple-400',
      bg: 'bg-purple-600/10',
      border: 'border-purple-500/20',
      glow: 'shadow-glow-purple',
      stroke: '#8b5cf6',
      fill: 'rgba(139, 92, 246, 0.1)'
    },
    cyan: {
      text: 'text-cyan-400',
      bg: 'bg-cyan-600/10',
      border: 'border-cyan-500/20',
      glow: 'shadow-glow-cyan',
      stroke: '#06b6d4',
      fill: 'rgba(6, 182, 212, 0.1)'
    },
    emerald: {
      text: 'text-emerald-400',
      bg: 'bg-emerald-600/10',
      border: 'border-emerald-500/20',
      glow: 'shadow-[0_0_15px_rgba(16,185,129,0.15)]',
      stroke: '#10b981',
      fill: 'rgba(16, 185, 129, 0.1)'
    },
    amber: {
      text: 'text-amber-400',
      bg: 'bg-amber-600/10',
      border: 'border-amber-500/20',
      glow: 'shadow-[0_0_15px_rgba(245,158,11,0.15)]',
      stroke: '#f59e0b',
      fill: 'rgba(245, 158, 11, 0.1)'
    }
  };

  const scheme = colors[color] || colors.purple;

  return (
    <div className={`glass glass-hover p-6 rounded-xl border ${scheme.border} flex flex-col justify-between h-44 shrink-0`}>
      {/* Top Header Row */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-gray-400">{title}</span>
        <div className={`p-2 rounded-lg ${scheme.bg} ${scheme.text}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {/* Main Stats Value */}
      <div className="flex items-end justify-between mt-2">
        <div>
          <h3 className="text-3xl font-extrabold text-white tracking-tight leading-none">{value}</h3>
          
          {change !== 0 && change !== undefined && (
            <div className="flex items-center gap-2 mt-2">
              <span className={`flex items-center text-xs font-bold ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
                {isPositive ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                <span>{Math.abs(change)}%</span>
              </span>
              <span className="text-[10px] text-gray-500 font-medium">vs yesterday</span>
            </div>
          )}
        </div>

        {/* Tiny Trend Sparkline */}
        {trendData && (
          <div className="w-24 h-12">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id={`grad-${title}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={scheme.stroke} stopOpacity={0.4}/>
                    <stop offset="95%" stopColor={scheme.stroke} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <Area 
                  type="monotone" 
                  dataKey="val" 
                  stroke={scheme.stroke} 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill={`url(#grad-${title})`} 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Bottom Confidence Row */}
      {confidence !== undefined && (
        <div className="mt-2 border-t border-gray-800/40 pt-2 flex items-center justify-between">
          <span className="text-[9px] text-gray-500 uppercase tracking-widest font-semibold">Sensor integrity</span>
          <ConfidenceBadge confidence={confidence} />
        </div>
      )}
    </div>
  );
}
