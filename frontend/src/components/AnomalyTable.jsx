import React from 'react';
import { AlertCircle, ShieldAlert, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function AnomalyTable({ anomalies, limit }) {
  const list = anomalies ? anomalies.slice(0, limit) : [];

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500/10 border-red-500/30 text-red-400';
      case 'high':
        return 'bg-orange-500/10 border-orange-500/30 text-orange-400';
      case 'medium':
        return 'bg-amber-500/10 border-amber-500/30 text-amber-400';
      default:
        return 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400';
    }
  };

  return (
    <div className="glass p-6 rounded-xl border border-gray-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Store Anomalies & Alert Logs</h3>
          <span className="text-[10px] text-gray-500 font-medium">Statistical deviation tracking & friction alarms</span>
        </div>
        <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">Active Monitoring</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-800/80 text-[10px] uppercase font-bold text-gray-500 tracking-wider">
              <th className="pb-3 pl-2">Severity</th>
              <th className="pb-3">Operational Event Description</th>
              <th className="pb-3">Timestamp</th>
              <th className="pb-3 pl-4">AI Recommended Intervention</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/40 text-xs">
            {list.map((an) => (
              <tr key={an.id} className="hover:bg-gray-800/20 transition-colors">
                {/* Severity Badge */}
                <td className="py-4 pl-2">
                  <span className={`px-2.5 py-0.5 rounded-full border text-[9px] font-bold uppercase tracking-wider ${getSeverityStyle(an.severity)}`}>
                    {an.severity}
                  </span>
                </td>

                {/* Description */}
                <td className="py-4 font-medium text-white max-w-sm pr-4">
                  <div className="flex items-start gap-2">
                    <ShieldAlert className="w-4 h-4 text-gray-500 shrink-0 mt-0.5" />
                    <span>{an.description}</span>
                  </div>
                </td>

                {/* Time */}
                <td className="py-4 text-gray-400 font-medium">
                  {new Date(an.detected_at).toLocaleTimeString('en-IN', {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                  })}
                </td>

                {/* Suggested Action */}
                <td className="py-4 pl-4 text-cyan-400 font-semibold max-w-md">
                  <div className="flex items-start gap-2">
                    <ArrowRight className="w-4 h-4 text-cyan-500 shrink-0 mt-0.5" />
                    <span>{an.suggested_action}</span>
                  </div>
                </td>
              </tr>
            ))}

            {list.length === 0 && (
              <tr>
                <td colSpan={4} className="py-8 text-center text-gray-500 font-semibold">
                  <CheckCircle2 className="w-8 h-8 text-emerald-500/40 mx-auto mb-2 animate-pulse" />
                  <span>No operational anomalies detected. System status nominal.</span>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
