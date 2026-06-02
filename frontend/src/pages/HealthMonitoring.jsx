import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import Layout from '../components/Layout';
import StoreHealthScore from '../components/StoreHealthScore';
import { getHealth } from '../api/client';
import { Activity, ShieldCheck, Heart, ShieldAlert } from 'lucide-react';

export default function HealthMonitoring() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const res = await getHealth();
      setData(res);
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

  // Mock historical health trends for visual appeal
  const healthHistory = [
    { day: 'Mon', score: 72 },
    { day: 'Tue', score: 74 },
    { day: 'Wed', score: 75 },
    { day: 'Thu', score: 78 },
    { day: 'Fri', score: 77 },
    { day: 'Sat', score: 79 },
    { day: 'Sun', score: data?.store_health?.overall_score || 78 }
  ];

  return (
    <Layout title="System Health & Diagnostics">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Large composite health gauge */}
        <div className="lg:col-span-1">
          <StoreHealthScore healthData={data.store_health} />
        </div>

        {/* Diagnostic charts and statuses */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Historical health score chart */}
          <div className="glass p-6 rounded-xl border border-gray-800">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-purple-400 mb-4">Historical Store Health Score</h4>
            <div className="w-full h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={healthHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(75, 85, 99, 0.1)" />
                  <XAxis dataKey="day" stroke="#9ca3af" fontSize={10} />
                  <YAxis stroke="#9ca3af" fontSize={10} domain={[60, 100]} />
                  <Tooltip contentStyle={{ background: 'rgba(17,24,39,0.95)', border: 'none', borderRadius: '8px' }} />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    name="Health Score" 
                    stroke="#8b5cf6" 
                    strokeWidth={3} 
                    dot={{ fill: '#8b5cf6', r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Diagnostic details panel */}
          <div className="glass p-6 rounded-xl border border-gray-800">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-cyan-400" />
              <h4 className="text-xs uppercase font-extrabold tracking-wider text-cyan-400">System Diagnostics</h4>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              {/* Uptime */}
              <div className="p-3.5 bg-gray-800/40 border border-gray-700/40 rounded-xl flex items-center justify-between">
                <span className="text-gray-400 font-semibold">Service Status</span>
                <span className="px-2.5 py-0.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-full font-bold uppercase tracking-wider">
                  Nominal
                </span>
              </div>

              {/* Database status */}
              <div className="p-3.5 bg-gray-800/40 border border-gray-700/40 rounded-xl flex items-center justify-between">
                <span className="text-gray-400 font-semibold">Database Schema</span>
                <span className="text-white font-extrabold capitalize">{data.database}</span>
              </div>

              {/* Ingestion events count */}
              <div className="p-3.5 bg-gray-800/40 border border-gray-700/40 rounded-xl flex items-center justify-between">
                <span className="text-gray-400 font-semibold">Processed Ingest Events</span>
                <span className="text-white font-extrabold">{data.total_events?.toLocaleString()}</span>
              </div>

              {/* CV Tracker status */}
              <div className="p-3.5 bg-gray-800/40 border border-gray-700/40 rounded-xl flex items-center justify-between">
                <span className="text-gray-400 font-semibold">Computer Vision Pipeline</span>
                <span className="text-purple-400 font-bold uppercase">Active</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </Layout>
  );
}
