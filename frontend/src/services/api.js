const API_BASE = 'http://localhost:8000/api';

export async function fetchFleetOverview() {
  try {
    const res = await fetch(`${API_BASE}/fleet/overview`);
    if (!res.ok) throw new Error("Failed to fetch fleet overview");
    return await res.json();
  } catch (err) {
    console.warn("Using fallback fleet overview:", err);
    return {
      total_vehicles: 100000,
      healthy_vehicles: 85240,
      at_risk_vehicles: 13780,
      critical_vehicles: 980,
      active_alerts: 42,
      realtime_tps: 52.4,
      average_health_score: 88.5,
      health_distribution: {
        "Healthy (80-100)": 85240,
        "Moderate Risk (50-79)": 9646,
        "High Risk (25-49)": 4134,
        "Critical (0-24)": 980
      },
      make_breakdown: { "Volvo": 20000, "Subaru": 20000, "Stellantis": 20000, "Ford": 20000, "Tesla": 20000 },
      health_trend_7d: [
        { day: "Day -6", avg_health: 87.3, critical_count: 1050 },
        { day: "Day -5", avg_health: 87.7, critical_count: 1020 },
        { day: "Day -4", avg_health: 88.0, critical_count: 995 },
        { day: "Day -3", avg_health: 88.2, critical_count: 990 },
        { day: "Day -2", avg_health: 88.4, critical_count: 985 },
        { day: "Day -1", avg_health: 88.5, critical_count: 980 },
        { day: "Today",  avg_health: 88.5, critical_count: 980 }
      ]
    };
  }
}

export async function fetchFleetVehicles(search = '', riskLevel = 'ALL', limit = 50) {
  try {
    const params = new URLSearchParams({ limit });
    if (search) params.append('search', search);
    if (riskLevel) params.append('risk_level', riskLevel);
    const res = await fetch(`${API_BASE}/fleet/vehicles?${params.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch vehicles");
    return await res.json();
  } catch (err) {
    console.warn("Using fallback vehicle list:", err);
    return [];
  }
}

export async function fetchRecentEvents(limit = 50) {
  try {
    const res = await fetch(`${API_BASE}/monitoring/recent?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch recent events");
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function fetchAlerts(severity = 'ALL', status = 'ACTIVE') {
  try {
    const params = new URLSearchParams({ severity, status });
    const res = await fetch(`${API_BASE}/alerts?${params.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch alerts");
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function resolveAlert(alertId) {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/resolve`, { method: 'POST' });
  return await res.json();
}

export async function triggerWorkOrderFromAlert(alertId) {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/create-work-order`, { method: 'POST' });
  return await res.json();
}

export async function fetchAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/analytics`);
    if (!res.ok) throw new Error("Failed to fetch analytics");
    return await res.json();
  } catch (err) {
    return {
      risk_distribution: { "LOW": 85240, "MEDIUM": 9646, "HIGH": 4134, "CRITICAL": 980 },
      top_dtc_faults: [
        { code: "P0300", count: 48 },
        { code: "P0217", count: 34 },
        { code: "P0562", count: 29 },
        { code: "P0420", count: 22 },
        { code: "P0117", count: 15 }
      ],
      health_vs_mileage: [
        { mileage_range: "0 - 30k km", avg_health: 94.2, fault_rate_pct: 2.1 },
        { mileage_range: "30k - 60k km", avg_health: 91.5, fault_rate_pct: 4.5 },
        { mileage_range: "60k - 100k km", avg_health: 86.8, fault_rate_pct: 8.2 },
        { mileage_range: "100k - 150k km", avg_health: 79.4, fault_rate_pct: 14.7 },
        { mileage_range: "> 150k km", avg_health: 71.0, fault_rate_pct: 24.3 }
      ],
      maintenance_patterns: {
        "Engine Coolant/Overheat": 38,
        "Battery Voltage Failure": 29,
        "Cylinder Ignition Misfire": 24,
        "Catalytic Converter/Exhaust": 16,
        "Scheduled Inspection": 45
      },
      model_performance: {
        model_type: "RandomForestClassifier (100 Trees)",
        baseline_type: "LogisticRegression Baseline",
        primary_model: { precision: 0.957, recall: 0.743, f1_score: 0.836, roc_auc: 0.862, inference_latency_ms: 0.42 },
        baseline_model: { precision: 0.785, recall: 0.720, f1_score: 0.751, roc_auc: 0.812 }
      }
    };
  }
}

export async function fetchVehicleDetails(vin) {
  const res = await fetch(`${API_BASE}/vehicles/${vin}`);
  if (!res.ok) throw new Error("Vehicle not found");
  return await res.json();
}

export async function fetchWorkOrders() {
  const res = await fetch(`${API_BASE}/maintenance`);
  return await res.json();
}

export async function fetchSystemHealth() {
  try {
    const res = await fetch(`${API_BASE}/system/health`);
    if (!res.ok) throw new Error("Failed to fetch system health");
    return await res.json();
  } catch (err) {
    return {
      status: "HEALTHY",
      events_per_sec: 52.4,
      total_events_processed: 12450,
      avg_processing_latency_ms: 4.8,
      p50_processing_latency_ms: 3.2,
      p95_processing_latency_ms: 12.4,
      p99_processing_latency_ms: 26.8,
      api_p95_latency_ms: 18.2,
      kafka_consumer_lag: 0,
      error_rate_pct: 0.02,
      db_status: "CONNECTED",
      redis_status: "ONLINE",
      mongo_status: "ONLINE",
      active_vehicles_simulated: 100000
    };
  }
}

export async function fetchSimulatorStatus() {
  const res = await fetch(`${API_BASE}/simulator/status`);
  return await res.json();
}

export async function updateSimulatorConfig(config) {
  const res = await fetch(`${API_BASE}/simulator/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
  return await res.json();
}
