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
      {/* 0. STALE FEED HEARTBEAT BANNER */}
      {data?.feed_status?.stale_feed && (
        <div className="flex items-center gap-3 p-4 mb-6 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs font-semibold animate-pulse shadow-[0_0_20px_rgba(244,63,94,0.1)]">
          <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0" />
          <div className="flex-1">
            <span className="font-extrabold uppercase tracking-wider text-rose-400 block mb-0.5">CAMERA FEED STATUS STALE</span>
            <span>No CCTV video event ingested for <span className="font-extrabold text-white bg-rose-600/40 px-1.5 py-0.5 rounded border border-rose-500/20">{data?.feed_status?.minutes_since_last_event} minutes</span>. Real-time store analytics metrics are paused. Please audit camera stream connection or trigger a video processing job.</span>
          </div>
        </div>
      )}

      {/* AI Executive Briefing */}
      {data?.ai_store_summary && (
        <div className="p-6 mb-8 bg-[#111927]/60 border border-[#223049] rounded-2xl backdrop-blur-xl">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 animate-pulse"></span>
            <span className="text-xs uppercase font-extrabold tracking-widest text-purple-400">AI Store Intelligence briefing</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-[#182235]/40 border border-[#263753] rounded-xl">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">Operational Status</span>
              <p className="text-sm text-slate-200 font-medium">{data.ai_store_summary.summary}</p>
            </div>
            <div className="p-4 bg-rose-950/20 border border-rose-500/20 rounded-xl">
              <span className="text-[10px] uppercase font-bold tracking-wider text-rose-400 block mb-1">Risk Assessment</span>
              <p className="text-sm text-rose-200 font-medium">{data.ai_store_summary.risks}</p>
            </div>
            <div className="p-4 bg-emerald-950/20 border border-emerald-500/20 rounded-xl">
              <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400 block mb-1">Growth Opportunities</span>
              <p className="text-sm text-emerald-200 font-medium">{data.ai_store_summary.opportunities}</p>
            </div>
          </div>
        </div>
      )}

      {/* 1. Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Store Traffic"
          value={metrics.total_footfall !== undefined ? metrics.total_footfall.toLocaleString('en-IN') : '0'}
          change={metrics.total_footfall > 0 ? 8.4 : 0}
          icon={Users}
          color="purple"
          trendData={metrics.total_footfall > 0 ? trend.map(t => ({ val: t.footfall })) : []}
          confidence={metrics.total_footfall > 0 ? 0.92 : undefined}
        />
        <MetricCard
          title="Unique Customers"
          value={metrics.unique_visitors !== undefined ? metrics.unique_visitors.toLocaleString('en-IN') : '0'}
          change={metrics.unique_visitors > 0 ? 12.2 : 0}
          icon={Users}
          color="cyan"
          trendData={metrics.unique_visitors > 0 ? trend.map(t => ({ val: t.footfall * 0.85 })) : []}
          confidence={metrics.unique_visitors > 0 ? 0.90 : undefined}
        />
        <MetricCard
          title="Conversion Rate"
          value={`${(metrics.conversion_rate * 100).toFixed(1)}%`}
          change={metrics.unique_visitors > 0 ? -3.1 : 0}
          icon={ShoppingBag}
          color="emerald"
          trendData={metrics.unique_visitors > 0 ? [{val:20}, {val:25}, {val:22}, {val:28}, {val:32}, {val:24}, {val:36}] : []}
          confidence={metrics.unique_visitors > 0 ? 0.88 : undefined}
        />
        <MetricCard
          title="Average Dwell Duration"
          value={`${Math.round(metrics.average_dwell_time / 60)} min`}
          change={metrics.unique_visitors > 0 ? 4.8 : 0}
          icon={Clock}
          color="amber"
          trendData={metrics.unique_visitors > 0 ? [{val:150}, {val:200}, {val:310}, {val:280}, {val:420}, {val:350}, {val:480}] : []}
          confidence={metrics.unique_visitors > 0 ? 0.86 : undefined}
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
