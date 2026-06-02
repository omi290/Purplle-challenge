import React, { useState } from 'react';
import { Flame, Clock, Users } from 'lucide-react';

export default function HeatmapGrid({ heatmapData }) {
  const zones = heatmapData?.zones || [];
  const [selectedZone, setSelectedZone] = useState(null);

  // Generate color mapping based on traffic intensity (0.0 to 1.0)
  const getIntensityColor = (intensity) => {
    if (intensity >= 0.8) return 'bg-red-500/20 border-red-500/40 text-red-300 shadow-[0_0_15px_rgba(239,68,68,0.15)]';
    if (intensity >= 0.5) return 'bg-orange-500/20 border-orange-500/40 text-orange-300 shadow-[0_0_15px_rgba(249,115,22,0.15)]';
    if (intensity >= 0.3) return 'bg-amber-500/20 border-amber-500/40 text-amber-300';
    return 'bg-purple-500/10 border-purple-500/20 text-purple-300';
  };

  return (
    <div className="glass p-6 rounded-xl border border-gray-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Store Layout Heatmap</h3>
          <span className="text-[10px] text-gray-500 font-medium">Zone traffic density & shopping session hotspots</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-red-500/10 border border-red-500/20 rounded-lg text-xs font-semibold text-red-400">
          <Flame className="w-4 h-4 text-red-500 animate-pulse" />
          <span>Real-time Density</span>
        </div>
      </div>

      {/* Dynamic Zone Heatmap Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Visual Map Layout Panel */}
        <div className="md:col-span-2 aspect-video bg-[#030712]/80 border border-gray-800 rounded-xl relative p-4 flex flex-col justify-between overflow-hidden shadow-inner">
          
          {/* Layout Grid Overlay */}
          <div className="absolute inset-0 grid grid-cols-6 grid-rows-6 pointer-events-none opacity-[0.02]">
            {Array.from({ length: 36 }).map((_, i) => (
              <div key={i} className="border border-white"></div>
            ))}
          </div>

          {/* Zones Rendered Positionally inside map boundary */}
          <div className="w-full h-full relative">
            {zones.map((zone) => {
              const c = zone.coordinates;
              const style = {
                left: `${c.x1 * 100}%`,
                top: `${c.y1 * 100}%`,
                width: `${(c.x2 - c.x1) * 100}%`,
                height: `${(c.y2 - c.y1) * 100}%`,
                position: 'absolute'
              };

              const activeColor = getIntensityColor(zone.intensity);

              return (
                <button
                  key={zone.zone_name}
                  style={style}
                  onClick={() => setSelectedZone(zone)}
                  className={`border rounded-lg p-3 transition-all duration-300 cursor-pointer flex flex-col justify-between text-left hover:scale-[1.01] hover:brightness-110 active:scale-95 ${activeColor}`}
                >
                  <span className="text-xs font-bold truncate tracking-tight uppercase block leading-none">{zone.zone_name}</span>
                  <div className="flex items-center justify-between text-[10px] font-semibold opacity-80 mt-1">
                    <span className="flex items-center gap-0.5"><Users className="w-3 h-3" />{zone.visitor_count}</span>
                    <span className="flex items-center gap-0.5"><Clock className="w-3 h-3" />{Math.round(zone.avg_dwell_seconds / 60)}m</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Zone Analysis Sidebar details */}
        <div className="glass p-5 rounded-xl border border-gray-800 flex flex-col justify-between min-h-[300px]">
          {selectedZone ? (
            <div className="space-y-4">
              <div>
                <span className="text-[10px] uppercase font-bold text-purple-400 tracking-wider">Active Selection</span>
                <h4 className="text-lg font-bold text-white mt-1 leading-none">{selectedZone.zone_name}</h4>
                <span className="text-xs text-gray-500 font-medium capitalize">Type: {selectedZone.zone_type} Zone</span>
              </div>

              <div className="space-y-3 pt-2">
                {/* Visitor Density count */}
                <div className="flex items-center justify-between p-3 bg-gray-800/40 border border-gray-700/50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-semibold text-gray-300">Unique Traffic</span>
                  </div>
                  <span className="text-sm font-bold text-white">{selectedZone.visitor_count} shoppers</span>
                </div>

                {/* Dwell time */}
                <div className="flex items-center justify-between p-3 bg-gray-800/40 border border-gray-700/50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-purple-400" />
                    <span className="text-xs font-semibold text-gray-300">Avg Dwell Duration</span>
                  </div>
                  <span className="text-sm font-bold text-white">{Math.round(selectedZone.avg_dwell_seconds / 60)} min {Math.round(selectedZone.avg_dwell_seconds % 60)}s</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-4">
              <Flame className="w-8 h-8 text-gray-600 mb-2 animate-bounce" />
              <span className="text-xs text-gray-400 font-semibold uppercase tracking-wider block">Zone Details Panel</span>
              <p className="text-[10px] text-gray-500 mt-1 max-w-[150px]">Click any layout zone on the heatmap map to view granular traffic analysis.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
