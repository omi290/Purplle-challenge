import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Filter, 
  Flame, 
  BarChart3, 
  Brain, 
  Activity, 
  Eye
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/funnel', label: 'Funnel Analysis', icon: Filter },
  { path: '/heatmap', label: 'Store Heatmap', icon: Flame },
  { path: '/analytics', label: 'Retail Analytics', icon: BarChart3 },
  { path: '/ai-insights', label: 'AI Suggested Actions', icon: Brain },
  { path: '/health', label: 'Health Monitoring', icon: Activity },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 h-full glass border-r border-gray-800 flex flex-col justify-between shrink-0">
      {/* Top Brand Banner */}
      <div>
        <div className="flex items-center gap-3 px-6 py-6 border-b border-gray-800">
          <div className="p-2 bg-purple-600/20 border border-purple-500/30 rounded-lg text-purple-500 shadow-glow-purple">
            <Eye className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold tracking-tight text-white leading-tight">Apex Retail</h1>
            <span className="text-xs text-purple-400 font-semibold tracking-wider uppercase">Intelligence OS</span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="mt-6 px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  isActive 
                    ? 'bg-purple-600/20 text-purple-400 border-l-4 border-purple-500 shadow-glow-purple' 
                    : 'text-gray-400 hover:bg-gray-800/40 hover:text-gray-200'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-purple-400' : 'text-gray-400'}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Branding */}
      <div className="px-6 py-4 border-t border-gray-800 text-center">
        <span className="text-[10px] text-gray-500 uppercase tracking-widest block">Operational Core</span>
        <span className="text-xs font-semibold text-gray-400 glow-cyan">v1.0.0 Stable</span>
      </div>
    </aside>
  );
}
