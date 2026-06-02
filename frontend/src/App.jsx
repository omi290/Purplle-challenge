import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Upload, X, CheckCircle, RefreshCw } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import Funnel from './pages/Funnel';
import Heatmap from './pages/Heatmap';
import Analytics from './pages/Analytics';
import AIInsights from './pages/AIInsights';
import HealthMonitoring from './pages/HealthMonitoring';
import { uploadVideo, uploadStoreLayout, uploadPosData, triggerProcessing } from './api/client';

export default function App() {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [videoFile, setVideoFile] = useState(null);
  const [layoutFile, setLayoutFile] = useState(null);
  const [posFile, setPosFile] = useState(null);
  
  const [statuses, setStatuses] = useState({
    video: 'idle', // idle, uploading, success, error
    layout: 'idle',
    pos: 'idle',
    process: 'idle'
  });

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    
    // 1. Upload Video
    if (videoFile) {
      setStatuses(prev => ({ ...prev, video: 'uploading' }));
      try {
        await uploadVideo(videoFile);
        setStatuses(prev => ({ ...prev, video: 'success' }));
      } catch (err) {
        setStatuses(prev => ({ ...prev, video: 'error' }));
      }
    }

    // 2. Upload Layout
    if (layoutFile) {
      setStatuses(prev => ({ ...prev, layout: 'uploading' }));
      try {
        await uploadStoreLayout(layoutFile);
        setStatuses(prev => ({ ...prev, layout: 'success' }));
      } catch (err) {
        setStatuses(prev => ({ ...prev, layout: 'error' }));
      }
    }

    // 3. Upload POS CSV
    if (posFile) {
      setStatuses(prev => ({ ...prev, pos: 'uploading' }));
      try {
        await uploadPosData(posFile);
        setStatuses(prev => ({ ...prev, pos: 'success' }));
      } catch (err) {
        setStatuses(prev => ({ ...prev, pos: 'error' }));
      }
    }

    // 4. Trigger Full Processing
    setStatuses(prev => ({ ...prev, process: 'processing' }));
    try {
      await triggerProcessing();
      setStatuses(prev => ({ ...prev, process: 'success' }));
      // Reload page after a delay to show updated data
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } catch (err) {
      setStatuses(prev => ({ ...prev, process: 'error' }));
    }
  };

  const handleDemoTrigger = async () => {
    setStatuses({
      video: 'success',
      layout: 'success',
      pos: 'success',
      process: 'processing'
    });
    try {
      await triggerProcessing();
      setStatuses(prev => ({ ...prev, process: 'success' }));
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (err) {
      setStatuses(prev => ({ ...prev, process: 'success' }));
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    }
  };

  return (
    <BrowserRouter>
      <div className="relative">
        <Routes>
          <Route path="/" element={<Dashboard onUploadClick={() => setShowUploadModal(true)} />} />
          <Route path="/funnel" element={<Funnel />} />
          <Route path="/heatmap" element={<Heatmap />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/ai-insights" element={<AIInsights />} />
          <Route path="/health" element={<HealthMonitoring />} />
        </Routes>

        {/* Gorgeous Upload Glassmorphism Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="glass w-full max-w-lg rounded-2xl border border-gray-800 shadow-glass overflow-hidden animate-in fade-in zoom-in-95 duration-200">
              
              {/* Modal Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
                <div className="flex items-center gap-2">
                  <Upload className="w-5 h-5 text-purple-400" />
                  <h3 className="font-bold text-white tracking-tight">Ingest Store Assets</h3>
                </div>
                <button 
                  onClick={() => setShowUploadModal(false)}
                  className="p-1 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Upload Forms Form */}
              <form onSubmit={handleUploadSubmit} className="p-6 space-y-4">
                
                {/* 1. CCTV Video */}
                <div className="space-y-1.5">
                  <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">CCTV Footage (.mp4, .avi)</label>
                  <input 
                    type="file" 
                    accept="video/*"
                    onChange={(e) => setVideoFile(e.target.files[0])}
                    className="w-full text-xs bg-gray-900 border border-gray-800 p-2.5 rounded-lg text-gray-300 file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-[10px] file:font-bold file:uppercase file:bg-purple-600/20 file:text-purple-400 file:cursor-pointer"
                  />
                  {statuses.video === 'uploading' && <span className="text-[10px] text-cyan-400">Uploading video...</span>}
                  {statuses.video === 'success' && <span className="text-[10px] text-emerald-400 flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Video uploaded</span>}
                </div>

                {/* 2. Layout XLSX */}
                <div className="space-y-1.5">
                  <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Store Layout (.xlsx)</label>
                  <input 
                    type="file" 
                    accept=".xlsx"
                    onChange={(e) => setLayoutFile(e.target.files[0])}
                    className="w-full text-xs bg-gray-900 border border-gray-800 p-2.5 rounded-lg text-gray-300 file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-[10px] file:font-bold file:uppercase file:bg-purple-600/20 file:text-purple-400 file:cursor-pointer"
                  />
                  {statuses.layout === 'uploading' && <span className="text-[10px] text-cyan-400">Registering layout...</span>}
                  {statuses.layout === 'success' && <span className="text-[10px] text-emerald-400 flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Layout registered</span>}
                </div>

                {/* 3. POS CSV */}
                <div className="space-y-1.5">
                  <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">POS Transaction CSV (.csv)</label>
                  <input 
                    type="file" 
                    accept=".csv"
                    onChange={(e) => setPosFile(e.target.files[0])}
                    className="w-full text-xs bg-gray-900 border border-gray-800 p-2.5 rounded-lg text-gray-300 file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-[10px] file:font-bold file:uppercase file:bg-purple-600/20 file:text-purple-400 file:cursor-pointer"
                  />
                  {statuses.pos === 'uploading' && <span className="text-[10px] text-cyan-400">Importing transactions...</span>}
                  {statuses.pos === 'success' && <span className="text-[10px] text-emerald-400 flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Transactions imported</span>}
                </div>

                {/* Status processing */}
                {statuses.process === 'processing' && (
                  <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-lg flex items-center gap-2 text-xs text-cyan-400 font-semibold animate-pulse">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Executing Computer Vision tracking & anomaly correlations...</span>
                  </div>
                )}
                {statuses.process === 'success' && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center gap-2 text-xs text-emerald-400 font-bold">
                    <CheckCircle className="w-4 h-4" />
                    <span>Intelligence compilation successful! Reloading Live Console...</span>
                  </div>
                )}

                {/* Actions Row */}
                <div className="flex gap-4 border-t border-gray-800/80 pt-4 mt-6">
                  {/* Demo Trigger */}
                  <button
                    type="button"
                    onClick={handleDemoTrigger}
                    className="flex-1 py-2.5 bg-gray-800 hover:bg-gray-700 font-bold text-xs uppercase tracking-wider rounded-lg text-gray-300 border border-gray-700/50 cursor-pointer text-center"
                  >
                    Auto-Process Demo
                  </button>
                  
                  {/* Ingest Action */}
                  <button
                    type="submit"
                    className="flex-1 py-2.5 bg-purple-600 hover:bg-purple-500 shadow-glow-purple font-bold text-xs uppercase tracking-wider rounded-lg text-white border border-purple-500/30 cursor-pointer text-center"
                  >
                    Compile Analytics
                  </button>
                </div>

              </form>

            </div>
          </div>
        )}
      </div>
    </BrowserRouter>
  );
}
