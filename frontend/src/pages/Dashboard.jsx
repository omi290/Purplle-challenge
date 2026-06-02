import React, { useState, useEffect } from 'react';
import { 
  Users, 
  ShoppingBag, 
  IndianRupee, 
  Clock, 
  AlertTriangle 
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

import Layout from '../components/Layout';
import MetricCard from '../components/MetricCard';
import StoreHealthScore from '../components/StoreHealthScore';
import RevenueLeakageMeter from '../components/RevenueLeakageMeter';
import OpportunityLossCard from '../components/OpportunityLossCard';
import AnomalyTable from '../components/AnomalyTable';
import AIInsightCard from '../components/AIInsightCard';
import { getDashboard } from '../api/client';

export default function Dashboard({ onUploadClick }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const res = await getDashboard();
      setData(res);
      setLoading(false);
    };
    fetchData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[#080d16] text-[#e2e8f0]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs uppercase font-bold tracking-widest text-purple-400">Loading Retail Intelligence...</span>
        </div>
      </div>
    );
  }

  const metrics = data?.metrics || {};
  const trend = data?.hourly_trend || [];
  const suggestions = data?.ai_suggestions || [];
  const anomalies = data?.recent_anomalies || [];

  return (
    <Layout title="Operations Live Console" onUploadClick={onUploadClick}>
      {/* 1. Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Store Traffic"
          value={metrics.total_footfall?.toLocaleString('en-IN')}
          change={8.4}
          icon={Users}
          color="purple"
          trendData={trend.map(t => ({ val: t.footfall }))}
          confidence={0.92}
        />
        <MetricCard
          title="Unique Customers"
          value={metrics.unique_visitors?.toLocaleString('en-IN')}
          change={12.2}
          icon={Users}
          color="cyan"
          trendData={trend.map(t => ({ val: t.footfall * 0.85 }))}
          confidence={0.90}
        />
        <MetricCard
          title="Conversion Rate"
          value={`${(metrics.conversion_rate * 100).toFixed(1)}%`}
          change={-3.1}
          icon={ShoppingBag}
          color="emerald"
          trendData={[{val:20}, {val:25}, {val:22}, {val:28}, {val:32}, {val:24}, {val:36}]}
          confidence={0.88}
        />
        <MetricCard
          title="Average Dwell Duration"
          value={`${Math.round(metrics.average_dwell_time / 60)} min`}
          change={4.8}
          icon={Clock}
          color="amber"
          trendData={[{val:150}, {val:200}, {val:310}, {val:280}, {val:420}, {val:350}, {val:480}]}
          confidence={0.86}
        />
      </div>

      {/* 2. Differentiator Widgets Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <StoreHealthScore healthData={data.store_health} />
        <RevenueLeakageMeter leakageData={data.revenue_leakage} />
        <OpportunityLossCard opportunityData={data.opportunity_loss} />
      </div>

      {/* 3. Time Series Traffic & Staff Chart */}
      <div className="glass p-6 rounded-xl border border-gray-800 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Visitor Traffic Trend (Today)</h3>
            <span className="text-[10px] text-gray-500 font-medium">Hourly shopper footfall correlated with active salespersons</span>
          </div>
          <span className="text-[10px] text-purple-400 font-bold uppercase tracking-widest bg-purple-500/10 border border-purple-500/20 px-3 py-1 rounded-lg">Brigade Bangalore</span>
        </div>
        
        <div className="w-full h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trend} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorFootfall" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(75, 85, 99, 0.15)" />
              <XAxis dataKey="hour" stroke="#9ca3af" fontSize={11} tickLine={false} />
              <YAxis stroke="#9ca3af" fontSize={11} tickLine={false} />
              <Tooltip 
                contentStyle={{ background: 'rgba(17,24,39,0.95)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px' }}
                labelStyle={{ fontWeight: 'bold', color: '#fff' }}
              />
              <Area 
                type="monotone" 
                dataKey="footfall" 
                name="Shopper Count"
                stroke="#8b5cf6" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorFootfall)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. AI Interventions Grids & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Suggestions */}
        <div className="lg:col-span-1 space-y-6">
          <div className="flex items-center gap-1.5 px-1">
            <AlertTriangle className="w-4.5 h-4.5 text-purple-400" />
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-purple-300">Live AI Interventions</h4>
          </div>
          <div className="space-y-4 max-h-[400px] overflow-y-auto pr-1">
            {suggestions.map((s, idx) => (
              <AIInsightCard key={idx} suggestion={s} />
            ))}
            {suggestions.length === 0 && (
              <div className="glass p-6 text-center text-gray-500 rounded-xl border border-gray-800">
                No active recommended actions. Store layout operations nominal.
              </div>
            )}
          </div>
        </div>

        {/* Right Alert Logs table */}
        <div className="lg:col-span-2">
          <AnomalyTable anomalies={anomalies} limit={4} />
        </div>
      </div>
    </Layout>
  );
}
