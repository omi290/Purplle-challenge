import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Download, 
  ShieldAlert, 
  Award, 
  PiggyBank, 
  RefreshCw, 
  AlertTriangle, 
  ArrowUpRight,
  Sparkles,
  Percent
} from 'lucide-react';

import Layout from '../components/Layout';
import StoreHealthScore from '../components/StoreHealthScore';
import { getDashboard, getAnomalies } from '../api/client';

export default function ExecutiveInsights({ onUploadClick }) {
  const [data, setData] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [leakageReduction, setLeakageReduction] = useState(50); // Slider: 0% to 100% reduction

  useEffect(() => {
    const fetchData = async () => {
      const dashRes = await getDashboard();
      const anomRes = await getAnomalies();
      setData(dashRes);
      setAnomalies(anomRes);
      setLoading(false);
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[#080d16] text-[#e2e8f0]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs uppercase font-bold tracking-widest text-purple-400">Loading Strategic Intelligence...</span>
        </div>
      </div>
    );
  }

  const metrics = data?.metrics || {};
  const health = data?.store_health || {};
  const leakage = data?.revenue_leakage || {};
  const opportunity = data?.opportunity_loss || {};
  const suggestions = data?.ai_suggestions || [];

  // 1. Math constants from live database correlation
  const leakedRevenue = leakage.estimated_leaked_revenue || 0;
  const lostCustomers = leakage.lost_customers || 0;
  const aov = leakage.average_basket_value || 0;
  const actualSales = leakage.actual_sales || 0;
  const uniqueVisitors = metrics.unique_visitors || 0;
  
  // 2. Simulated recovery math based on interactive slider
  const savedCustomers = Math.round(lostCustomers * (leakageReduction / 100));
  const recoveredRevenue = savedCustomers * aov;
  const potentialTotalSales = actualSales + leakedRevenue;
  const simulatedSales = actualSales + recoveredRevenue;
  
  // Simulate new conversion rate
  const currentTxns = Math.round(uniqueVisitors * metrics.conversion_rate);
  const simulatedTxns = currentTxns + savedCustomers;
  const simulatedConversion = uniqueVisitors > 0 ? (simulatedTxns / uniqueVisitors) * 100 : 0;

  const handlePrint = () => {
    window.print();
  };

  return (
    <Layout title="Executive Insights & Strategy" onUploadClick={onUploadClick}>
      
      {/* 0. Top Controls Row */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8 no-print">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-purple-400">Strategic Decision Dashboard</h3>
          <p className="text-[10px] text-gray-500 font-semibold tracking-wider uppercase">Projected Recoveries, Friction Audits, & Layout Opportunities</p>
        </div>
        
        <button
          onClick={handlePrint}
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 active:scale-95 transition-all text-xs font-bold text-white rounded-xl shadow-glow-purple border border-purple-500/20 cursor-pointer"
        >
          <Download className="w-4 h-4" />
          <span>Export Executive PDF</span>
        </button>
      </div>

      {/* Printable Report Header */}
      <div className="hidden print:block mb-8 border-b border-gray-300 pb-6">
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-black text-purple-900">APEX Retail Intelligence OS</h1>
            <p className="text-sm font-bold text-gray-600 uppercase tracking-widest mt-1">Executive Performance & Strategic Operations Audit</p>
          </div>
          <div className="text-right text-xs font-bold text-gray-500">
            <span>Date: {new Date().toLocaleDateString('en-IN', { dateStyle: 'long' })}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* ==========================================
            LEFT COLUMN: Store Health & What-If Simulator
           ========================================== */}
        <div className="lg:col-span-1 space-y-8 print:col-span-3">
          
          {/* Store Health Gauge */}
          <div className="glass p-6 rounded-2xl border border-gray-800/80 shadow-glass">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-purple-400 mb-4 border-b border-gray-800/50 pb-2">Store Health Audit</h4>
            <StoreHealthScore healthData={health} />
          </div>

          {/* Interactive What-If Revenue Simulator */}
          <div className="glass p-6 rounded-2xl border border-purple-800/40 shadow-glass bg-gradient-to-br from-purple-950/10 to-indigo-950/5 no-print">
            <div className="flex items-center justify-between mb-4 border-b border-gray-800/50 pb-2">
              <h4 className="text-xs uppercase font-extrabold tracking-wider text-cyan-400">What-If Revenue Simulator</h4>
              <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
            </div>
            
            <p className="text-[11px] text-gray-400 leading-relaxed mb-6">
              Simulate operational improvements. Drag the slider to model the impact of reducing checkout wait times and recovery cash.
            </p>

            <div className="space-y-6">
              {/* Slider Input */}
              <div className="space-y-2">
                <div className="flex justify-between text-[10px] font-extrabold text-gray-400 uppercase tracking-wider">
                  <span>Billing Abandonment Reduction</span>
                  <span className="text-cyan-400 font-black">{leakageReduction}%</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={leakageReduction}
                  onChange={(e) => setLeakageReduction(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-gray-900 border border-gray-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                />
                <div className="flex justify-between text-[9px] text-gray-500 font-bold">
                  <span>0% (As Is)</span>
                  <span>100% (No Friction)</span>
                </div>
              </div>

              {/* Simulation Output Cards */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-950/60 border border-gray-800/60 rounded-xl space-y-1">
                  <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider block">Recovered Revenue</span>
                  <span className="text-lg font-black text-emerald-400 glow-emerald">₹{recoveredRevenue.toLocaleString('en-IN')}</span>
                </div>
                <div className="p-3 bg-gray-950/60 border border-gray-800/60 rounded-xl space-y-1">
                  <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider block">Shoppers Saved</span>
                  <span className="text-lg font-black text-cyan-400 glow-cyan">+{savedCustomers}</span>
                </div>
              </div>

              {/* Conversion rate simulated delta */}
              <div className="p-3 bg-gray-950/60 border border-purple-800/20 rounded-xl space-y-1 text-center">
                <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider block">Simulated Conversion Rate</span>
                <div className="flex items-center justify-center gap-2">
                  <span className="text-lg font-black text-white">{simulatedConversion.toFixed(1)}%</span>
                  <span className="text-[10px] font-extrabold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded">
                    +{(simulatedConversion - (metrics.conversion_rate * 100)).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* ==========================================
            RIGHT COLUMN: Strategic Opportunities & Recommended Actions
           ========================================== */}
        <div className="lg:col-span-2 space-y-8 print:col-span-3">
          
          {/* Revenue Recovery target logs */}
          <div className="glass p-6 rounded-2xl border border-gray-800/80 shadow-glass">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-cyan-400 mb-4 border-b border-gray-800/50 pb-2">Financial Impact Auditing</h4>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              
              {/* Actual Sales */}
              <div className="p-4 bg-gray-900/40 border border-gray-800/60 rounded-xl flex items-center gap-3">
                <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400">
                  <PiggyBank className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[9px] font-extrabold text-gray-500 uppercase tracking-wider block">Today's Sales Revenue</span>
                  <span className="text-base font-black text-white">₹{actualSales.toLocaleString('en-IN')}</span>
                </div>
              </div>

              {/* Leaked Sales */}
              <div className="p-4 bg-gray-900/40 border border-gray-800/60 rounded-xl flex items-center gap-3">
                <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 animate-pulse">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[9px] font-extrabold text-gray-500 uppercase tracking-wider block">Potential Leaked Sales</span>
                  <span className="text-base font-black text-rose-400">₹{leakedRevenue.toLocaleString('en-IN')}</span>
                </div>
              </div>

              {/* Projected Total */}
              <div className="p-4 bg-gray-900/40 border border-purple-800/30 rounded-xl flex items-center gap-3 bg-gradient-to-br from-purple-900/5 to-purple-800/0">
                <div className="p-2.5 bg-purple-500/10 border border-purple-500/20 rounded-lg text-purple-400">
                  <ArrowUpRight className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-[9px] font-extrabold text-gray-500 uppercase tracking-wider block">Target Potential Sales</span>
                  <span className="text-base font-black text-purple-300">₹{potentialTotalSales.toLocaleString('en-IN')}</span>
                </div>
              </div>

            </div>

            {/* Simulated target bar representation */}
            <div className="mt-6 space-y-2">
              <div className="flex justify-between text-[9px] font-bold text-gray-500 uppercase tracking-wider">
                <span>Revenue Target Progression</span>
                <span>{((simulatedSales / potentialTotalSales) * 100).toFixed(0)}% Achieved</span>
              </div>
              <div className="w-full h-2.5 bg-gray-950 rounded-full border border-gray-800/80 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 via-indigo-500 to-cyan-400 transition-all duration-300"
                  style={{ width: `${(simulatedSales / potentialTotalSales) * 100}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-[8px] text-gray-500 font-semibold tracking-wider uppercase pt-1">
                <span>Current Sales: ₹{actualSales.toLocaleString('en-IN')}</span>
                <span>Simulated Target: ₹{Math.round(simulatedSales).toLocaleString('en-IN')}</span>
                <span>Frictionless Target: ₹{potentialTotalSales.toLocaleString('en-IN')}</span>
              </div>
            </div>
          </div>

          {/* Top Opportunities List */}
          <div className="glass p-6 rounded-2xl border border-gray-800/80 shadow-glass">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-purple-400 mb-4 border-b border-gray-800/50 pb-2">Top Opportunities & Strategic Risks</h4>
            
            <div className="space-y-4">
              
              {/* Opportunity 1: Category traffic drop-offs */}
              <div className="p-4 bg-gray-900/30 border border-gray-800/80 rounded-xl flex flex-col sm:flex-row justify-between sm:items-center gap-4">
                <div className="space-y-1">
                  <span className="text-[10px] font-extrabold text-purple-400 uppercase tracking-wider block">Shelf Attraction Risk</span>
                  <h5 className="text-xs font-bold text-white uppercase">{opportunity.top_opportunity_zone || "Makeup Zone"} Dwell Bottlenecks</h5>
                  <p className="text-[10px] text-gray-400 normal-case leading-relaxed">
                    Dwell-to-purchase conversions are lagging behind layout averages. Potential leakage estimated at <b>₹{Math.round(opportunity.estimated_revenue_impact * 0.4 || 30000).toLocaleString('en-IN')}</b>.
                  </p>
                </div>
                <span className="px-3 py-1 text-[10px] font-bold bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-lg uppercase tracking-wider shrink-0 text-center">
                  Score: {Math.round(opportunity.total_opportunities_lost / 10 || 62)} Loss
                </span>
              </div>

              {/* Opportunity 2: Billing abandonment */}
              <div className="p-4 bg-gray-900/30 border border-gray-800/80 rounded-xl flex flex-col sm:flex-row justify-between sm:items-center gap-4">
                <div className="space-y-1">
                  <span className="text-[10px] font-extrabold text-cyan-400 uppercase tracking-wider block">Billing Queue Friction</span>
                  <h5 className="text-xs font-bold text-white uppercase">Checkout Abandonment Losses</h5>
                  <p className="text-[10px] text-gray-400 normal-case leading-relaxed">
                    Shoppers joining checkout billing line exited due to wait time congestion. Leaked Order Count: <b>{lostCustomers} customers</b>.
                  </p>
                </div>
                <span className="px-3 py-1 text-[10px] font-bold bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg uppercase tracking-wider shrink-0 text-center">
                  ₹{leakedRevenue.toLocaleString('en-IN')} Leaked
                </span>
              </div>

            </div>
          </div>

          {/* Action Recommendations Drawer (Full AI Reasoning details) */}
          <div className="glass p-6 rounded-2xl border border-gray-800/80 shadow-glass">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-emerald-400 mb-4 border-b border-gray-800/50 pb-2">Recommended Operational Interventions</h4>
            
            <div className="space-y-4">
              {suggestions.map((s, idx) => (
                <div key={idx} className="p-4 bg-gray-800/40 border border-gray-700/30 rounded-xl space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase px-2.5 py-0.5 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-full">
                      Match Score: {Math.round(s.confidence * 100)}%
                    </span>
                    <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border ${
                      s.severity === 'critical' ? 'bg-red-500/10 border-red-500/20 text-red-400' :
                      s.severity === 'high' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' :
                      'bg-cyan-500/10 border-cyan-500/20 text-cyan-400'
                    }`}>
                      {s.severity} Severity
                    </span>
                  </div>
                  
                  <div className="space-y-1">
                    <h5 className="text-xs font-bold text-white uppercase">{s.anomaly_type.replace('_', ' ')} Suggestion</h5>
                    <p className="text-[10px] text-gray-300 normal-case leading-relaxed font-semibold">
                      {s.suggestion}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[9px] uppercase font-bold text-gray-500 border-t border-gray-800/40 pt-2.5 mt-1">
                    <div>
                      <span className="text-[8px] tracking-wider text-gray-500">AI Operational Rationale</span>
                      <p className="text-gray-300 font-normal normal-case leading-relaxed mt-0.5">
                        {s.ai_recommendation?.reasoning || "Friction threshold exceeded baseline tolerance averages."}
                      </p>
                    </div>
                    <div>
                      <span className="text-[8px] tracking-wider text-gray-500">Target Business Impact</span>
                      <p className="text-gray-300 font-normal normal-case leading-relaxed mt-0.5">
                        {s.ai_recommendation?.expected_business_impact || "Improves checkout transaction conversions and shelf dwell rates."}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              
              {suggestions.length === 0 && (
                <div className="p-6 text-center text-gray-500 text-xs font-semibold">
                  All category operations nominal. No active recovery recommendations at this time.
                </div>
              )}
            </div>
          </div>

        </div>

      </div>

    </Layout>
  );
}
