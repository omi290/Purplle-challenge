import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

export default function Layout({ children, title, onUploadClick }) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#080d16] text-[#e2e8f0]">
      {/* Sidebar navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header toolbar */}
        <Header title={title} onUploadClick={onUploadClick} />
        
        {/* Dashboard page scroll viewport */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-gradient-to-b from-[#0a111e] to-[#080d16]">
          {children}
        </main>
      </div>
    </div>
  );
}
