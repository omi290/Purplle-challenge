import React from 'react';
import { Upload, Calendar, RotateCcw } from 'lucide-react';
import LiveIndicator from './LiveIndicator';
import { resetDatabase } from '../api/client';

export default function Header({ title, onUploadClick }) {
  const dateStr = new Date().toLocaleDateString('en-IN', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  const handleReset = async () => {
    if (window.confirm("Are you sure you want to reset the store OS console back to zero metrics? This will wipe the database tables.")) {
      try {
        await resetDatabase();
        window.location.reload();
      } catch (err) {
        alert("Failed to reset database: " + err.message);
      }
    }
  };

  return (
    <header className="h-16 glass border-b border-gray-800 flex items-center justify-between px-8 shrink-0">
      {/* Title & Live Status */}
      <div className="flex items-center gap-4">
        <h2 className="text-xl font-bold tracking-tight text-white">{title}</h2>
        <LiveIndicator />
      </div>

      {/* Header Actions */}
      <div className="flex items-center gap-4">
        {/* Date Display */}
        <div className="flex items-center gap-2 px-4 py-2 bg-gray-800/40 border border-gray-700/50 rounded-lg text-xs font-semibold text-gray-300">
          <Calendar className="w-4 h-4 text-cyan-400" />
          <span>{dateStr}</span>
        </div>

        {/* Reset Button */}
        <button
          onClick={handleReset}
          className="flex items-center gap-2 px-4 py-2 bg-[#181d2a]/60 hover:bg-[#20273a] active:scale-95 transition-all text-xs font-semibold text-rose-400 border border-rose-500/20 hover:border-rose-500/40 rounded-lg"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset Console</span>
        </button>

        {/* Action Button */}
        <button
          onClick={onUploadClick}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 active:scale-95 transition-all text-xs font-semibold text-white rounded-lg shadow-glow-purple border border-purple-500/30"
        >
          <Upload className="w-4 h-4" />
          <span>Upload CCTV & Layout</span>
        </button>
      </div>
    </header>
  );
}

