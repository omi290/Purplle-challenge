import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import HeatmapGrid from '../components/HeatmapGrid';
import { getHeatmap } from '../api/client';
import { Flame, Clock, Users, ShieldCheck } from 'lucide-react';

export default function Heatmap({ onUploadClick }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const res = await getHeatmap();
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

  const zones = data?.zones || [];

  return (
    <Layout title="Layout Heatmap Analysis" onUploadClick={onUploadClick}>
      <div className="space-y-8">
        {/* Heatmap Grid Panel */}
        <HeatmapGrid heatmapData={data} />

        {/* Zone Traffic Rankings & Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Top Traffic Zones */}
          <div className="glass p-6 rounded-xl border border-gray-800">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-purple-400 mb-4">Traffic Densities By Zone</h4>
            <div className="space-y-3.5">
              {zones.map((zone) => (
                <div key={zone.zone_name} className="flex items-center justify-between text-xs border-b border-gray-800/40 pb-2">
                  <span className="text-gray-300 font-semibold uppercase">{zone.zone_name}</span>
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1 text-gray-400 font-medium">
                      <Users className="w-3.5 h-3.5 text-cyan-400" />
                      <span>{zone.visitor_count}</span>
                    </span>
                    <span className="flex items-center gap-1 text-gray-400 font-medium w-16 justify-end">
                      <Clock className="w-3.5 h-3.5 text-purple-400" />
                      <span>{Math.round(zone.avg_dwell_seconds / 60)}m</span>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Dwell Heatmap Analysis */}
          <div className="glass p-6 rounded-xl border border-gray-800 flex flex-col justify-between">
            <div>
              <h4 className="text-xs uppercase font-extrabold tracking-wider text-cyan-400 mb-2">Zone Dwell Insights</h4>
              <p className="text-xs text-gray-400 leading-relaxed">
                Makeup cosmetics zones (e.g. Lipsticks, foundations) show highest traffic count (620 unique) and average dwell times (240 seconds). Skincare browsing is steady, whereas Haircare zones are experiencing low traffic density thresholds.
              </p>
            </div>
            
            <div className="border-t border-gray-800/60 pt-4 mt-4 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-purple-400 shrink-0" />
              <div className="text-[10px] text-gray-500">
                Heatmaps coordinate scales are mapped using auto-parsed store layout spreadsheets (`store_layout.xlsx`) uploaded during initialization.
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </Layout>
  );
}
