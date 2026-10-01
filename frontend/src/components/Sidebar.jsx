import React from 'react';
import { 
  LayoutDashboard, 
  Activity, 
  HeartPulse, 
  Bell, 
  BarChart3, 
  Truck, 
  Server, 
  Wrench 
} from 'lucide-react';

export default function Sidebar({ activePage, setActivePage }) {
  const navItems = [
    { id: 'overview', name: 'Fleet Overview', icon: LayoutDashboard },
    { id: 'monitoring', name: 'Live Monitoring', icon: Activity, badge: 'LIVE' },
    { id: 'health', name: 'Vehicle Health', icon: HeartPulse },
    { id: 'alerts', name: 'Alerts', icon: Bell },
    { id: 'analytics', name: 'Analytics & ML', icon: BarChart3 },
    { id: 'vehicle', name: 'Vehicle Details', icon: Truck },
    { id: 'system', name: 'System Health', icon: Server }
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 min-h-[calc(100vh-4rem)] flex flex-col justify-between border-r border-slate-800 p-4">
      <div className="space-y-6">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 px-3">
          Operations & Intelligence
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-slate-800 text-white font-semibold border-l-4 border-blue-500'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="bg-emerald-500/20 text-emerald-400 text-[10px] font-bold px-1.5 py-0.5 rounded animate-pulse">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Enterprise Fleet Info Footer */}
      <div className="bg-slate-800/60 rounded-lg p-3 text-xs border border-slate-700/50 space-y-1">
        <div className="font-semibold text-slate-200">Vehicure Engine</div>
        <div className="text-slate-400 text-[11px]">v1.0.0 (Production)</div>
        <div className="text-slate-500 text-[10px]">Polyglot DB & Stream Processing</div>
      </div>
    </aside>
  );
}
