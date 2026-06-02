import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function StoreHealthScore({ healthData }) {
  const score = healthData?.overall_score || 0;
  const grade = healthData?.grade || 'N/A';
  const components = healthData?.components || {};

  // Pie chart data representing progress
  const chartData = [
    { value: score },
    { value: 100 - score }
  ];

  let color = '#10b981'; // Emerald
  let shadow = 'shadow-[0_0_20px_rgba(16,185,129,0.3)]';
  if (score < 40) {
    color = '#ef4444'; // Red
    shadow = 'shadow-[0_0_20px_rgba(239,68,68,0.3)]';
  } else if (score < 70) {
    color = '#f59e0b'; // Amber
    shadow = 'shadow-[0_0_20px_rgba(245,158,11,0.3)]';
  }

  const componentLabels = {
    conversion_rate: "Conversion Rate",
    dwell_quality: "Dwell Quality",
    queue_efficiency: "Queue Efficiency",
    zone_utilization: "Zone Utilization",
    anomaly_rate: "System Stability",
    revenue_efficiency: "Sales Volume Value"
  };

  return (
    <div className="glass p-6 rounded-xl border border-gray-800 flex flex-col justify-between h-[450px]">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Store Health Score</h3>
        <span className="text-[10px] text-gray-500 font-medium">Weighted composite efficiency index</span>
      </div>

      {/* Circular Progress Gauge */}
      <div className="relative w-48 h-48 mx-auto flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={85}
              startAngle={90}
              endAngle={-270}
              dataKey="value"
            >
              <Cell fill={color} />
              <Cell fill="rgba(31, 41, 55, 0.3)" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* Floating Center Score */}
        <div className="absolute text-center">
          <span className="text-4xl font-black text-white tracking-tight glow-purple">{score}</span>
          <div className="text-[10px] uppercase tracking-widest text-purple-400 font-bold mt-1">Grade {grade}</div>
        </div>
      </div>

      {/* Components List Breakdown */}
      <div className="space-y-2 border-t border-gray-800/60 pt-4">
        {Object.entries(components).map(([key, item]) => (
          <div key={key} className="flex items-center justify-between text-xs">
            <span className="text-gray-400 font-medium">{componentLabels[key] || key}</span>
            <div className="flex items-center gap-3">
              {/* Horizontal tiny bar */}
              <div className="w-16 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-purple-500 rounded-full" 
                  style={{ width: `${item.score}%` }}
                ></div>
              </div>
              <span className="font-bold text-white w-8 text-right">{item.score}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
