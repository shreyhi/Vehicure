import React, { useState, useEffect } from 'react';
import { Bell, CheckCircle, Wrench, AlertTriangle, ShieldAlert } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { fetchAlerts, resolveAlert, triggerWorkOrderFromAlert } from '../services/api';

export default function AlertsPage({ onSelectVehicle }) {
  const [alerts, setAlerts] = useState([]);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ACTIVE');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, [severityFilter, statusFilter]);

  async function loadAlerts() {
    try {
      const data = await fetchAlerts(severityFilter, statusFilter);
      setAlerts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleResolve(id) {
    await resolveAlert(id);
    loadAlerts();
  }

  async function handleCreateWorkOrder(id) {
    await triggerWorkOrderFromAlert(id);
    alert("Preventive maintenance work order triggered successfully!");
    loadAlerts();
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Alerts & Diagnostic Management</h1>
        <p className="text-xs text-slate-500 mt-1">
          Automated alert engine flagging vehicle health anomalies, critical DTCs, and failure probabilities.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="saas-card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-600">Severity:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1 rounded-md text-xs font-semibold ${
                severityFilter === sev ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-600">Status:</span>
          {['ACTIVE', 'RESOLVED', 'ALL'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-md text-xs font-semibold ${
                statusFilter === st ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {alerts.length === 0 ? (
          <div className="saas-card text-center py-10 text-slate-400 text-xs">
            No active alerts matching the selected filters.
          </div>
        ) : (
          alerts.map((a) => (
            <div key={a.id} className="saas-card flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4">
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center space-x-3">
                  <span className="text-xs font-mono font-bold text-slate-500">{a.id}</span>
                  <StatusBadge level={a.severity} />
                  {a.dtc_code && (
                    <span className="bg-red-100 text-red-700 font-mono text-[11px] font-bold px-2 py-0.5 rounded">
                      DTC: {a.dtc_code}
                    </span>
                  )}
                  <span className="text-xs text-slate-400">{a.created_at}</span>
                </div>

                <div className="text-sm font-bold text-slate-900">{a.reason}</div>
                <div className="text-xs text-slate-600">
                  <span className="font-semibold text-slate-700">Recommended Action:</span> {a.recommended_action}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onSelectVehicle(a.vin)}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg text-xs font-semibold"
                >
                  View Vehicle
                </button>

                {a.status === 'ACTIVE' && (
                  <>
                    <button
                      onClick={() => handleCreateWorkOrder(a.id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1"
                    >
                      <Wrench className="w-3.5 h-3.5" />
                      <span>Work Order</span>
                    </button>

                    <button
                      onClick={() => handleResolve(a.id)}
                      className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1"
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>Resolve</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
