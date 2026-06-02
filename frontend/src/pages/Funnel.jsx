import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import FunnelChart from '../components/FunnelChart';
import { getFunnel } from '../api/client';
import { ArrowRightCircle, AlertCircle, ShoppingBag, ShieldCheck } from 'lucide-react';

export default function Funnel({ onUploadClick }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const res = await getFunnel();
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

  const stages = data?.stages || [];

  return (
    <Layout title="Conversion Funnel Analysis" onUploadClick={onUploadClick}>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Side: Funnel Chart Visualization */}
        <div className="lg:col-span-2 space-y-6">
          <FunnelChart funnelData={data} />
          
          {/* Confidence-Aware Analytics notice */}
          <div className="glass p-5 rounded-xl border border-gray-800 flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-purple-400 shrink-0" />
            <div className="text-xs">
              <span className="font-bold text-white block">Confidence-Aware Tracking</span>
              <span className="text-gray-400">Our CV tracking pipeline assigns an operational confidence index (currently {Math.round(data.confidence * 100)}%) across all visual checkout calculations.</span>
            </div>
          </div>
        </div>

        {/* Right Side: Stage Breakdown Details */}
        <div className="space-y-6">
          <div className="glass p-6 rounded-xl border border-gray-800">
            <h4 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">Stage Friction Points</h4>
            
            <div className="space-y-4">
              {stages.slice(1).map((stage, idx) => (
                <div key={stage.name} className="p-4 bg-gray-800/40 border border-gray-700/40 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white uppercase">{stage.name} Transition</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 bg-red-500/10 border border-red-500/20 text-red-400 rounded-full">
                      -{stage.drop_off}% Loss
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-400 leading-relaxed">
                    {stage.name === "Browse" && "15% of visitors bounced right after entering, indicating storefront visual marketing or initial layouts need refinement."}
                    {stage.name === "Billing Queue" && "A massive 45% drop occurred between browsing and joining queue. This marks major layout bottlenecks in cosmetics browsing."}
                    {stage.name === "Purchase" && "3.6% of queue members abandoned checkout prior to transaction logs. Indicates cashier queue bottlenecks."}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="glass p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-purple-900/10 to-purple-800/5">
            <ShoppingBag className="w-8 h-8 text-purple-400 mb-3" />
            <h4 className="text-sm font-bold text-white mb-2">Overall Store Conversion</h4>
            <div className="text-3xl font-black text-white glow-purple">{(data.overall_conversion * 100).toFixed(1)}%</div>
            <p className="text-[10px] text-gray-500 mt-2 leading-relaxed">
              Standard beauty stores aim for 35% conversion. Operational actions are automatically generated under AI Suggested Actions to assist store managers.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
