import React, { useState, useEffect } from 'react';
import { Truck, AlertTriangle, ShieldAlert, CheckCircle, Wrench, ArrowLeft, Activity, Gauge } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { fetchVehicleDetails } from '../services/api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function VehicleDetails({ vin, onBack }) {
  const [vehicle, setVehicle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!vin) return;
    async function load() {
      try {
        setLoading(true);
        const data = await fetchVehicleDetails(vin);
        setVehicle(data);
      } catch (err) {
        setError("Vehicle not found");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [vin]);

  if (!vin) {
    return (
      <div className="saas-card text-center py-12 text-slate-500 text-xs">
        Select a vehicle from the Fleet Overview, Live Stream, or Health view to inspect details.
      </div>
    );
  }

  if (loading) {
    return (
      <div className="saas-card text-center py-12 text-slate-500 text-xs">
        Loading vehicle profile and telemetry history for VIN {vin}...
      </div>
    );
  }

  const exp = vehicle?.prediction_explanation || {};

  return (
    <div className="space-y-6">
      {/* Navigation Header */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onBack}
          className="p-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <span>{vehicle?.make} {vehicle?.model} ({vehicle?.year})</span>
            <StatusBadge level={vehicle?.risk_level} />
          </h1>
          <div className="text-xs font-mono text-slate-500 mt-0.5">VIN: {vehicle?.vin} | Fleet: {vehicle?.fleet_name}</div>
        </div>
      </div>

      {/* Top Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Health Gauge & Score */}
        <div className="saas-card flex flex-col justify-between space-y-3 bg-slate-900 text-white border-slate-800">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Vehicle Health Score</div>
          <div className="flex items-baseline space-x-2">
            <span className={`text-5xl font-black ${
              vehicle?.health_score < 40 ? 'text-red-500' : vehicle?.health_score < 70 ? 'text-amber-400' : 'text-emerald-400'
            }`}>
              {vehicle?.health_score}
            </span>
            <span className="text-xl text-slate-400 font-bold">/ 100</span>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-800 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Failure Risk Score:</span>
              <span className="font-bold text-red-400">{vehicle?.risk_score}/100</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Failure Probability:</span>
              <span className="font-bold text-amber-400">{vehicle?.failure_prob}%</span>
            </div>
          </div>
        </div>

        {/* Prediction Explanations */}
        <div className="saas-card md:col-span-2 space-y-3 border-amber-200 bg-amber-50/30">
          <div className="flex items-center space-x-2 text-amber-800 font-bold text-sm">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>Predictive Risk Explanation & Key Factors</span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="font-semibold text-slate-700">Main Reasons:</div>
            <ul className="list-disc list-inside space-y-1 text-slate-800 font-medium pl-1">
              {exp?.main_reasons?.map((reason, idx) => (
                <li key={idx} className="text-slate-800">
                  {reason}
                </li>
              ))}
            </ul>
          </div>

          <div className="pt-2 border-t border-amber-200/60 flex items-center justify-between text-xs">
            <div>
              <span className="font-semibold text-slate-700">Recommended Action: </span>
              <span className="font-bold text-red-700">{exp?.recommended_action}</span>
            </div>

            <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1">
              <Wrench className="w-3.5 h-3.5" />
              <span>Schedule Service</span>
            </button>
          </div>
        </div>
      </div>

      {/* Telemetry Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Temperature & Battery History Chart */}
        <div className="saas-card space-y-4">
          <h2 className="text-sm font-bold text-slate-900">Engine Temperature & Battery History</h2>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={vehicle?.telemetry_history || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="timestamp" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip />
                <Line type="monotone" dataKey="engine_temp" stroke="#ef4444" strokeWidth={2} name="Engine Temp (°C)" />
                <Line type="monotone" dataKey="battery_voltage" stroke="#3b82f6" strokeWidth={2} name="Battery (V)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Speed History Chart */}
        <div className="saas-card space-y-4">
          <h2 className="text-sm font-bold text-slate-900">Vehicle Speed Stream (km/h)</h2>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={vehicle?.telemetry_history || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="timestamp" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip />
                <Line type="monotone" dataKey="speed_kmh" stroke="#10b981" strokeWidth={2} name="Speed (km/h)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Diagnostic Faults & Maintenance Log */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="saas-card space-y-3">
          <h2 className="text-sm font-bold text-slate-900">Active Diagnostic Fault Codes (DTC)</h2>
          {vehicle?.active_alerts?.length === 0 ? (
            <div className="text-xs text-slate-400 py-4">No active diagnostic codes reported.</div>
          ) : (
            <div className="space-y-2">
              {vehicle?.active_alerts?.map((alt) => (
                <div key={alt.id} className="p-3 bg-red-50/50 border border-red-200 rounded-lg text-xs flex justify-between items-center">
                  <div>
                    <div className="font-bold text-red-900">{alt.dtc_code || 'FAULT'}: {alt.reason}</div>
                    <div className="text-slate-500 text-[11px]">{alt.created_at}</div>
                  </div>
                  <StatusBadge level={alt.severity} />
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="saas-card space-y-3">
          <h2 className="text-sm font-bold text-slate-900">Preventive Maintenance Log</h2>
          {vehicle?.maintenance_history?.length === 0 ? (
            <div className="text-xs text-slate-400 py-4">No prior maintenance orders recorded for this vehicle.</div>
          ) : (
            <div className="space-y-2">
              {vehicle?.maintenance_history?.map((m) => (
                <div key={m.id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs flex justify-between items-center">
                  <div>
                    <div className="font-bold text-slate-900">{m.title}</div>
                    <div className="text-slate-500 text-[11px]">Scheduled: {m.scheduled_date}</div>
                  </div>
                  <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded">
                    {m.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
