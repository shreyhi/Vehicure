import React, { useState, useEffect } from 'react';
import { ShieldCheck, Activity, Radio, Cpu, RefreshCw } from 'lucide-react';
import { fetchSimulatorStatus } from '../services/api';

export default function Navbar({ activePage, setActivePage }) {
  const [simStatus, setSimStatus] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await fetchSimulatorStatus();
        setSimStatus(data);
      } catch (err) {}
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="bg-slate-900 text-white p-2 rounded-lg flex items-center justify-center font-bold tracking-wider text-sm shadow-xs">
          <Activity className="w-5 h-5 text-emerald-400 mr-1.5 animate-pulse" />
          VEHICURE
        </div>
        <div className="h-5 w-[1px] bg-slate-200" />
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
          Vehicure Intelligence Platform
        </span>
      </div>

      {/* Simulator Real-Time Live Status Indicator */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          <span className="text-slate-600">Simulator:</span>
          <span className="font-semibold text-slate-900">100,000 Connected Vehicles</span>
          <span className="text-slate-400">|</span>
          <span className="text-emerald-700 font-semibold">{simStatus?.target_tps || 50} events/sec</span>
        </div>

        {/* System Health Quick Pill */}
        <button
          onClick={() => setActivePage('system')}
          className="flex items-center space-x-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors"
        >
          <Cpu className="w-4 h-4" />
          <span>System Healthy</span>
        </button>
      </div>
    </header>
  );
}
