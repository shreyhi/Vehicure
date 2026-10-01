import React from 'react';

export default function MetricCard({ title, value, subtitle, icon: Icon, trend, color = 'slate' }) {
  const borderColors = {
    slate: 'border-slate-200',
    red: 'border-red-200 bg-red-50/20',
    amber: 'border-amber-200 bg-amber-50/20',
    emerald: 'border-emerald-200 bg-emerald-50/20',
    blue: 'border-blue-200 bg-blue-50/20'
  };

  const iconColors = {
    slate: 'text-slate-600 bg-slate-100',
    red: 'text-red-600 bg-red-100',
    amber: 'text-amber-600 bg-amber-100',
    emerald: 'text-emerald-600 bg-emerald-100',
    blue: 'text-blue-600 bg-blue-100'
  };

  return (
    <div className={`saas-card ${borderColors[color]} flex flex-col justify-between`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-lg ${iconColors[color]}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold text-slate-900 tracking-tight">{value}</div>
        {subtitle && <div className="text-xs text-slate-500 mt-1">{subtitle}</div>}
      </div>

      {trend && (
        <div className={`text-[11px] font-semibold mt-3 ${trend.startsWith('+') ? 'text-red-600' : 'text-emerald-600'}`}>
          {trend} vs last 24h
        </div>
      )}
    </div>
  );
}
