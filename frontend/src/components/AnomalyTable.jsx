import React, { useState } from 'react';
import { AlertCircle, ShieldAlert, ArrowRight, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';

export default function AnomalyTable({ anomalies, limit }) {
  const [expandedId, setExpandedId] = useState(null);
  const list = anomalies ? anomalies.slice(0, limit) : [];

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500/10 border-red-500/30 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.1)]';
      case 'high':
        return 'bg-orange-500/10 border-orange-500/30 text-orange-400';
      case 'medium':
        return 'bg-amber-500/10 border-amber-500/30 text-amber-400';
      default:
        return 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400';
    }
  };

  const handleResolve = async (id, e) => {
    // Stop propagation so it doesn't expand/collapse the row
    e.stopPropagation();
    const feedback = window.prompt("Enter Manager Resolution Note:");
    if (feedback === null) return;
    const disagreed = window.confirm("Do you disagree with the AI suggested action?");
    try {
      const res = await fetch(`http://localhost:8000/api/anomalies/${id}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          manager_feedback: feedback || "Resolved without comment",
          disagreed: disagreed
        })
      });
      if (res.ok) {
        window.location.reload();
      } else {
        alert("Failed to resolve anomaly.");
      }
    } catch (err) {
      alert("Error: " + err);
    }
  };

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
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
              <th className="pb-3 text-right pr-2">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/40 text-xs">
            {list.map((an) => {
              const isExpanded = expandedId === an.id;
              const rec = an.ai_recommendation || {};
              const recText = rec.recommendation || an.suggested_action || "Perform general store layout audit.";

              return (
                <React.Fragment key={an.id}>
                  {/* Clickable Row */}
                  <tr 
                    onClick={() => toggleExpand(an.id)}
                    className={`hover:bg-gray-800/20 transition-all cursor-pointer select-none ${isExpanded ? 'bg-purple-950/5' : ''}`}
                  >
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
                        <span className={an.resolved ? "text-gray-400 font-normal line-through opacity-70" : ""}>{an.description}</span>
                      </div>
                    </td>

                    {/* Time */}
                    <td className="py-4 text-gray-400 font-medium whitespace-nowrap">
                      {new Date(an.detected_at).toLocaleTimeString('en-IN', {
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                      })}
                    </td>

                    {/* Suggested Action preview */}
                    <td className="py-4 pl-4 text-cyan-400 font-semibold max-w-md">
                      <div className="flex items-start gap-2">
                        <ArrowRight className="w-4 h-4 text-cyan-500 shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <span className={an.resolved ? "line-through text-gray-500 opacity-60 font-normal" : ""}>
                            {recText}
                          </span>
                          {!an.resolved && (
                            <span className="inline-flex items-center gap-0.5 text-[8px] text-purple-400 font-bold uppercase tracking-wider ml-2 bg-purple-500/10 border border-purple-500/20 px-1.5 py-0.5 rounded">
                              {isExpanded ? <ChevronUp className="w-2.5 h-2.5" /> : <ChevronDown className="w-2.5 h-2.5" />}
                              <span>AI details</span>
                            </span>
                          )}
                        </div>
                      </div>
                      {an.resolved && an.manager_feedback && (
                        <div className="text-[10px] text-purple-400 font-medium italic mt-1 pl-6">
                          Feedback: "{an.manager_feedback}" {an.disagreed && <span className="text-red-500 font-bold ml-1">(Disagreed)</span>}
                        </div>
                      )}
                    </td>

                    {/* Actions column */}
                    <td className="py-4 text-right pr-2">
                      {an.resolved ? (
                        <span className="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] rounded-lg font-bold uppercase">
                          Actioned
                        </span>
                      ) : (
                        <button
                          onClick={(e) => handleResolve(an.id, e)}
                          className="px-2.5 py-1 bg-purple-600 hover:bg-purple-500 text-[10px] rounded-lg text-white font-bold uppercase transition-all active:scale-95 cursor-pointer border border-purple-500/20"
                        >
                          Resolve
                        </button>
                      )}
                    </td>
                  </tr>

                  {/* Expandable Dropdown Drawer */}
                  {isExpanded && !an.resolved && (
                    <tr className="bg-purple-950/5">
                      <td colSpan={5} className="p-4 border-t border-b border-gray-800/80">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-[10px] uppercase font-bold text-gray-400">
                          {/* 1. Reasoning Card */}
                          <div className="bg-[#030712]/60 p-3.5 rounded-xl border border-gray-800/80 space-y-1 shadow-inner">
                            <span className="text-purple-400 font-extrabold tracking-wider">AI Operational Reasoning</span>
                            <p className="text-gray-300 font-normal normal-case leading-relaxed pt-1.5">
                              {rec.reasoning || `Flagged based on operational metric value of ${an.metric_value} exceeding threshold ${an.threshold_value}.`}
                            </p>
                          </div>
                          
                          {/* 2. Business Impact Card */}
                          <div className="bg-[#030712]/60 p-3.5 rounded-xl border border-gray-800/80 space-y-1 shadow-inner">
                            <span className="text-cyan-400 font-extrabold tracking-wider">Expected Business Impact</span>
                            <p className="text-gray-300 font-normal normal-case leading-relaxed pt-1.5">
                              {rec.expected_business_impact || "Enhances shopper dwell metrics, optimizes categories, and reduces checkout friction."}
                            </p>
                          </div>

                          {/* 3. Recommendation Match & Progress score */}
                          <div className="bg-[#030712]/60 p-3.5 rounded-xl border border-gray-800/80 space-y-1 shadow-inner flex flex-col justify-between">
                            <div>
                              <span className="text-emerald-400 font-extrabold tracking-wider">AI Recommendation Match</span>
                              <div className="flex items-center gap-2 mt-2">
                                <div className="flex-1 h-2 bg-gray-900 rounded-full overflow-hidden border border-gray-800">
                                  <div 
                                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full" 
                                    style={{ width: `${(rec.confidence || an.confidence) * 100}%` }}
                                  ></div>
                                </div>
                                <span className="text-[10px] font-black text-white">{Math.round((rec.confidence || an.confidence) * 100)}%</span>
                              </div>
                            </div>
                            <span className="text-[8px] text-gray-500 lowercase tracking-wider italic normal-case block pt-2">
                              Note: click row again to collapse details panel
                            </span>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}

            {list.length === 0 && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-gray-500 font-semibold">
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
