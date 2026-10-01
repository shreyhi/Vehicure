import React, { useState, useEffect } from 'react';
import { Activity, Pause, Play, Filter, AlertTriangle, ShieldCheck } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { fetchRecentEvents } from '../services/api';

export default function LiveMonitoring({ onSelectVehicle }) {
  const [events, setEvents] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [vinSearch, setVinSearch] = useState('');

  useEffect(() => {
    if (isPaused) return;

    // Connect to SSE event stream
    const eventSource = new EventSource('http://localhost:8000/api/monitoring/stream');
    
    eventSource.onmessage = (e) => {
      try {
        const eventData = JSON.parse(e.data);
        setEvents((prev) => [eventData, ...prev.slice(0, 150)]);
      } catch (err) {}
    };

    // Fallback polling if SSE fails
    const fallbackInterval = setInterval(async () => {
      try {
        const recent = await fetchRecentEvents(40);
        if (recent && recent.length > 0) {
          setEvents(recent);
        }
      } catch (err) {}
    }, 1500);

    return () => {
      eventSource.close();
      clearInterval(fallbackInterval);
    };
  }, [isPaused]);

  const filteredEvents = events.filter((e) => {
    if (filterSeverity !== 'ALL' && e.computed_risk_level !== filterSeverity) return false;
    if (vinSearch && !e.vin.toLowerCase().includes(vinSearch.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header & Stream Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-slate-900">Live Vehicle Telemetry Stream</h1>
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Real-time incoming vehicle signals processed through deduplication, validation & ML risk engine.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              isPaused
                ? 'bg-emerald-50 border-emerald-300 text-emerald-700 hover:bg-emerald-100'
                : 'bg-amber-50 border-amber-300 text-amber-700 hover:bg-amber-100'
            }`}
          >
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
            <span>{isPaused ? 'Resume Stream' : 'Pause Stream'}</span>
          </button>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="saas-card p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">Severity Filter:</span>

          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setFilterSeverity(lvl)}
              className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
                filterSeverity === lvl
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>

        <div>
          <input
            type="text"
            placeholder="Filter by VIN..."
            value={vinSearch}
            onChange={(e) => setVinSearch(e.target.value)}
            className="px-3 py-1 bg-slate-50 border border-slate-200 rounded-lg text-xs w-48 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Live Stream Table */}
      <div className="saas-card overflow-x-auto p-0">
        <table className="saas-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Vehicle VIN</th>
              <th>Seq #</th>
              <th>Speed</th>
              <th>Engine Temp</th>
              <th>Battery</th>
              <th>DTC Codes</th>
              <th>Status</th>
              <th>Risk Level</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvents.length === 0 ? (
              <tr>
                <td colSpan={10} className="text-center py-8 text-slate-400 text-xs">
                  Waiting for incoming telemetry events from vehicle simulator stream...
                </td>
              </tr>
            ) : (
              filteredEvents.map((e, idx) => (
                <tr
                  key={`${e.vin}-${e.seq}-${idx}`}
                  className={`transition-colors cursor-pointer ${
                    e.computed_risk_level === 'CRITICAL' ? 'bg-red-50/40 hover:bg-red-50/80' : ''
                  }`}
                  onClick={() => onSelectVehicle(e.vin)}
                >
                  <td className="text-slate-500 font-mono text-xs">
                    {e.timestamp ? e.timestamp.split('T')[1].split('.')[0] : 'Just now'}
                  </td>
                  <td className="font-mono text-xs text-blue-600 font-semibold">{e.vin}</td>
                  <td className="font-mono text-slate-500 text-xs">#{e.seq}</td>
                  <td className="font-medium">{e.speed_kmh} km/h</td>
                  <td className={`font-semibold ${e.engine_temp > 105 ? 'text-red-600 font-bold' : ''}`}>
                    {e.engine_temp}°C
                  </td>
                  <td className={`font-semibold ${e.battery_voltage < 11.5 ? 'text-amber-600 font-bold' : ''}`}>
                    {e.battery_voltage} V
                  </td>
                  <td>
                    {e.dtc_codes && e.dtc_codes.length > 0 ? (
                      <span className="bg-red-100 text-red-700 text-[10px] font-mono font-bold px-1.5 py-0.5 rounded">
                        {e.dtc_codes.join(', ')}
                      </span>
                    ) : (
                      <span className="text-slate-400 text-[10px]">None</span>
                    )}
                  </td>
                  <td>
                    <span className="text-xs text-slate-600">{e.vehicle_status}</span>
                  </td>
                  <td>
                    <StatusBadge level={e.computed_risk_level || 'LOW'} />
                  </td>
                  <td>
                    <button
                      onClick={(evt) => {
                        evt.stopPropagation();
                        onSelectVehicle(e.vin);
                      }}
                      className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-0.5 rounded text-xs font-medium"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
