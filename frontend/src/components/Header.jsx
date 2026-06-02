import React from 'react';
import { Upload, Calendar, RefreshCw } from 'lucide-react';
import LiveIndicator from './LiveIndicator';

export default function Header({ title, onUploadClick }) {
  const dateStr = new Date().toLocaleDateString('en-IN', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

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
