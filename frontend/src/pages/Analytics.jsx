import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import Layout from '../components/Layout';
import { getMetrics } from '../api/client';
import { BarChart3, Users, Clock, ShoppingBag } from 'lucide-react';

export default function Analytics({ onUploadClick }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const res = await getMetrics();
      setMetrics(res);
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

  const zoneData = metrics.zone_metrics || [];
  const peakHours = metrics.peak_hours || [];
  
  // Staff vs Customer distribution data
  const staffCustData = [
    { name: 'Active Customers', value: metrics.customer_count, color: '#8b5cf6' },
    { name: 'Store Employees', value: metrics.staff_count, color: '#06b6d4' }
  ];

  return (
    <Layout title="Retail Intelligence Analytics" onUploadClick={onUploadClick}>
      <div className="space-y-8">
        
        {/* Hourly footfalls and Staff vs Customer rows */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Hourly distribution bar chart */}
          <div className="glass p-6 rounded-xl border border-gray-800 lg:col-span-2">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-purple-400 mb-4">Traffic Peaks By Hour</h4>
            <div className="w-full h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={peakHours}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(75, 85, 99, 0.1)" />
                  <XAxis dataKey="hour" stroke="#9ca3af" fontSize={10} />
                  <YAxis stroke="#9ca3af" fontSize={10} />
                  <Tooltip contentStyle={{ background: 'rgba(17,24,39,0.95)', border: 'none', borderRadius: '8px' }} />
                  <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Staff vs Customer donut */}
          <div className="glass p-6 rounded-xl border border-gray-800">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-cyan-400 mb-4">Active Staff Distribution</h4>
            <div className="w-full h-48 relative flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={staffCustData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={65}
                    dataKey="value"
                  >
                    {staffCustData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute text-center">
                <span className="text-2xl font-black text-white">{metrics.staff_count}</span>
                <span className="text-[9px] uppercase tracking-wider font-bold text-gray-400 block">Employees</span>
              </div>
            </div>
            {/* Custom Legends */}
            <div className="space-y-2 mt-4">
              {staffCustData.map((entry, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }}></div>
                    <span className="text-gray-400 font-semibold">{entry.name}</span>
                  </div>
                  <span className="font-extrabold text-white">{entry.value}</span>
                </div>
              ))}
            </div>
          </div>
          
        </div>

        {/* Zone Traffic & dwell comparisons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Zone Traffic comparison */}
          <div className="glass p-6 rounded-xl border border-gray-800">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-emerald-400 mb-4">Zone Attraction Rates</h4>
            <div className="w-full h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={zoneData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(75, 85, 99, 0.1)" />
                  <XAxis type="number" stroke="#9ca3af" fontSize={10} />
                  <YAxis dataKey="zone_name" type="category" stroke="#9ca3af" fontSize={10} width={80} />
                  <Tooltip contentStyle={{ background: 'rgba(17,24,39,0.95)', border: 'none', borderRadius: '8px' }} />
                  <Bar dataKey="visitor_count" fill="#10b981" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Dwell time distributions */}
          <div className="glass p-6 rounded-xl border border-gray-800">
            <h4 className="text-xs uppercase font-extrabold tracking-wider text-amber-400 mb-4">Avg Dwell time comparison</h4>
            <div className="w-full h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={zoneData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(75, 85, 99, 0.1)" />
                  <XAxis dataKey="zone_name" stroke="#9ca3af" fontSize={10} />
                  <YAxis stroke="#9ca3af" fontSize={10} />
                  <Tooltip contentStyle={{ background: 'rgba(17,24,39,0.95)', border: 'none', borderRadius: '8px' }} />
                  <Bar dataKey="avg_dwell_seconds" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>

      </div>
    </Layout>
  );
}
