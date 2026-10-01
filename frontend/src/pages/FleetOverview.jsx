import React, { useState, useEffect } from 'react';
import { Truck, ShieldAlert, AlertTriangle, CheckCircle, Radio, Activity, Search } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import StatusBadge from '../components/StatusBadge';
import { fetchFleetOverview, fetchFleetVehicles } from '../services/api';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid } from 'recharts';

export default function FleetOverview({ onSelectVehicle }) {
  const [overview, setOverview] = useState(null);
  const [vehicles, setVehicles] = useState([]);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, [search, riskFilter]);

  async function loadData() {
    try {
      const [ovData, vehData] = await Promise.all([
        fetchFleetOverview(),
        fetchFleetVehicles(search, riskFilter, 25)
      ]);
      setOverview(ovData);
      setVehicles(vehData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Fleet Health & Operations Overview</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time monitoring and predictive maintenance analytics across 100,000+ connected vehicles.
          </p>
        </div>
        <div className="flex items-center space-x-2 bg-white border border-slate-200 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 shadow-xs">
          <Activity className="w-4 h-4 text-emerald-500 animate-pulse" />
          <span>Stream Ingestion: {overview?.realtime_tps || 50} events/sec</span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Total Vehicles"
          value={overview?.total_vehicles?.toLocaleString() || "100,000"}
          subtitle="Monitored in Real-Time"
          icon={Truck}
          color="slate"
        />
        <MetricCard
          title="Healthy Vehicles"
          value={overview?.healthy_vehicles?.toLocaleString() || "85,240"}
          subtitle={`${Math.round(((overview?.healthy_vehicles || 85240) / 100000) * 100)}% of fleet operational`}
          icon={CheckCircle}
          color="emerald"
        />
        <MetricCard
          title="At-Risk Vehicles"
          value={overview?.at_risk_vehicles?.toLocaleString() || "13,780"}
          subtitle="Moderate & High Failure Risk"
          icon={AlertTriangle}
          color="amber"
        />
        <MetricCard
          title="Critical Vehicles"
          value={overview?.critical_vehicles?.toLocaleString() || "980"}
          subtitle="Immediate Action Required"
          icon={ShieldAlert}
          color="red"
        />
        <MetricCard
          title="Active Alerts"
          value={overview?.active_alerts || 42}
          subtitle="Unresolved Diagnostics"
          icon={Radio}
          color="blue"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Fleet Health Trend Chart */}
        <div className="saas-card lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">7-Day Fleet Health Score Trend</h2>
              <p className="text-xs text-slate-500">Average overall health score across all connected vehicle models</p>
            </div>
            <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">
              Avg Score: {overview?.average_health_score || 88.5}/100
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={overview?.health_trend_7d || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis domain={[75, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip />
                <Area type="monotone" dataKey="avg_health" stroke="#0284c7" fill="#e0f2fe" strokeWidth={2} name="Health Score" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Level Distribution */}
        <div className="saas-card space-y-4">
          <h2 className="text-sm font-bold text-slate-900">Fleet Risk Breakdown</h2>
          <p className="text-xs text-slate-500">Current failure risk level proportions</p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={Object.entries(overview?.health_distribution || {}).map(([key, val]) => ({ name: key.split(' ')[0], count: val }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top High-Risk Vehicles Action Table */}
      <div className="saas-card space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Prioritized At-Risk Vehicles</h2>
            <p className="text-xs text-slate-500">Vehicles ranked by predictive failure probability & risk score</p>
          </div>

          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search VIN, make, model..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs w-64 focus:outline-none focus:border-blue-500"
              />
            </div>

            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-lg text-xs px-3 py-1.5 focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="LOW">Low Risk</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="saas-table">
            <thead>
              <tr>
                <th>Vehicle VIN</th>
                <th>Make & Model</th>
                <th>Fleet</th>
                <th>Health Score</th>
                <th>Failure Prob (%)</th>
                <th>Engine Temp</th>
                <th>Battery</th>
                <th>Risk Level</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {vehicles.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-6 text-slate-400 text-xs">
                    No matching vehicles found.
                  </td>
                </tr>
              ) : (
                vehicles.map((v) => (
                  <tr key={v.vin} className="cursor-pointer" onClick={() => onSelectVehicle(v.vin)}>
                    <td className="font-mono text-xs text-blue-600 font-semibold">{v.vin}</td>
                    <td className="font-medium text-slate-900">{v.make} {v.model} ({v.year})</td>
                    <td className="text-slate-500">{v.fleet_name}</td>
                    <td>
                      <span className={`font-bold ${v.health_score < 40 ? 'text-red-600' : v.health_score < 70 ? 'text-amber-600' : 'text-emerald-600'}`}>
                        {v.health_score}/100
                      </span>
                    </td>
                    <td className="font-semibold">{v.failure_prob}%</td>
                    <td>{v.last_engine_temp}°C</td>
                    <td>{v.last_battery_voltage} V</td>
                    <td><StatusBadge level={v.risk_level} /></td>
                    <td>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectVehicle(v.vin);
                        }}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1 rounded text-xs font-semibold"
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
    </div>
  );
}
