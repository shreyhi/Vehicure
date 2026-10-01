import React, { useState, useEffect } from 'react';
import { HeartPulse, Search, Filter, AlertOctagon, ShieldAlert } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { fetchFleetVehicles } from '../services/api';

export default function VehicleHealth({ onSelectVehicle }) {
  const [vehicles, setVehicles] = useState([]);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVehicles();
  }, [search, riskFilter]);

  async function loadVehicles() {
    try {
      const data = await fetchFleetVehicles(search, riskFilter, 50);
      setVehicles(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Vehicle Health & Risk Scoring</h1>
        <p className="text-xs text-slate-500 mt-1">
          Predictive failure scores computed combining domain rule engines and scikit-learn ML models.
        </p>
      </div>

      {/* Filter controls */}
      <div className="saas-card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by VIN, vehicle model, OEM..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-600">Risk Category:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setRiskFilter(lvl)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                riskFilter === lvl
                  ? 'bg-slate-900 text-white border-slate-900'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Vehicle Grid List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {vehicles.map((v) => (
          <div
            key={v.vin}
            onClick={() => onSelectVehicle(v.vin)}
            className="saas-card hover:border-slate-400 cursor-pointer flex flex-col justify-between space-y-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xs font-mono font-bold text-blue-600">{v.vin}</div>
                <div className="text-sm font-bold text-slate-900 mt-0.5">{v.make} {v.model}</div>
                <div className="text-[11px] text-slate-500">{v.fleet_name} ({v.year})</div>
              </div>
              <StatusBadge level={v.risk_level} />
            </div>

            {/* Health Bar */}
            <div className="space-y-1.5 bg-slate-50 p-3 rounded-lg border border-slate-100">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 font-medium">Health Score:</span>
                <span className="font-bold text-slate-900">{v.health_score}/100</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    v.health_score > 75 ? 'bg-emerald-500' : v.health_score > 45 ? 'bg-amber-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${v.health_score}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-xs pt-1">
                <span className="text-slate-500">Failure Prob:</span>
                <span className="font-semibold text-red-600">{v.failure_prob}%</span>
              </div>
            </div>

            {/* Sub Metrics */}
            <div className="grid grid-cols-3 gap-2 text-center text-xs border-t border-slate-100 pt-3">
              <div>
                <div className="text-slate-400 text-[10px] uppercase">Engine</div>
                <div className="font-semibold text-slate-800">{v.last_engine_temp}°C</div>
              </div>
              <div>
                <div className="text-slate-400 text-[10px] uppercase">Battery</div>
                <div className="font-semibold text-slate-800">{v.last_battery_voltage} V</div>
              </div>
              <div>
                <div className="text-slate-400 text-[10px] uppercase">Odometer</div>
                <div className="font-semibold text-slate-800">{Math.round(v.odometer_km).toLocaleString()} km</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
