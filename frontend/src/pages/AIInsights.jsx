import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import AIInsightCard from '../components/AIInsightCard';
import AnomalyTable from '../components/AnomalyTable';
import { getAnomalies, getDashboard } from '../api/client';
import { Brain, Sparkles, History, ShieldAlert } from 'lucide-react';

export default function AIInsights() {
  const [anomalies, setAnomalies] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const anomRes = await getAnomalies();
      const dashRes = await getDashboard();
      setAnomalies(anomRes);
      setSuggestions(dashRes?.ai_suggestions || []);
      setLoading(false);
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[#080d16] text-[#e2e8f0]">
        <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <Layout title="AI Suggested Actions">
      <div className="space-y-8">
        
        {/* Suggested actions grids */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-purple-300">Live AI Interventions</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {suggestions.map((s, idx) => (
              <AIInsightCard key={idx} suggestion={s} />
            ))}
            
            {suggestions.length === 0 && (
              <div className="glass p-6 text-center text-gray-500 rounded-xl border border-gray-800 md:col-span-3">
                No active recommended actions at this time. All retail metrics nominal.
              </div>
            )}
          </div>
        </div>

        {/* Dynamic anomaly list */}
        <div className="space-y-4 pt-4">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-300">Anomaly Audit Logs</h3>
          </div>
          
          <AnomalyTable anomalies={anomalies} />
        </div>

      </div>
    </Layout>
  );
}
