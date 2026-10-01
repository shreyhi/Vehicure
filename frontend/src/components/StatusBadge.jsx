import React from 'react';

export default function StatusBadge({ level }) {
  const normalized = (level || 'LOW').toUpperCase();

  const styles = {
    CRITICAL: 'bg-red-50 text-red-700 border-red-200 font-bold',
    HIGH: 'bg-amber-50 text-amber-700 border-amber-200 font-semibold',
    MEDIUM: 'bg-yellow-50 text-yellow-700 border-yellow-200 font-medium',
    LOW: 'bg-emerald-50 text-emerald-700 border-emerald-200 font-medium',
    HEALTHY: 'bg-emerald-50 text-emerald-700 border-emerald-200 font-medium',
    ACTIVE: 'bg-blue-50 text-blue-700 border-blue-200 font-medium',
    RESOLVED: 'bg-slate-100 text-slate-600 border-slate-200 font-medium',
  };

  const currentStyle = styles[normalized] || styles.LOW;

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs border ${currentStyle}`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
        normalized === 'CRITICAL' ? 'bg-red-600 animate-pulse' :
        normalized === 'HIGH' ? 'bg-amber-600' :
        normalized === 'MEDIUM' ? 'bg-yellow-600' : 'bg-emerald-600'
      }`} />
      {normalized}
    </span>
  );
}
