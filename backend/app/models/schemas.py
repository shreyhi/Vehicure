from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TelemetryEvent(BaseModel):
    vin: str = Field(..., example="1HGCM82633A004352")
    timestamp: str = Field(..., example="2026-09-30T10:15:02.120Z")
    lat: float = Field(..., example=21.1702)
    lon: float = Field(..., example=72.8311)
    speed_kmh: float = Field(..., example=64.2)
    engine_temp: float = Field(..., example=92.5)
    battery_voltage: float = Field(..., example=12.6)
    fuel_level_pct: float = Field(..., example=75.0)
    odometer_km: float = Field(..., example=45230.5)
    dtc_codes: List[str] = Field(default=[], example=["P0301"])
    harsh_braking: bool = Field(default=False)
    harsh_accel: bool = Field(default=False)
    vehicle_status: str = Field(default="MOVING")
    seq: int = Field(..., example=88412)

class VehicleSummary(BaseModel):
    vin: str
    make: str
    model: str
    year: int
    fleet_name: str
    health_score: float
    risk_score: float
    risk_level: str
    failure_prob: float
    odometer_km: float
    last_speed_kmh: float
    last_engine_temp: float
    last_battery_voltage: float
    last_seen: str
    status: str

class VehicleDetail(VehicleSummary):
    latitude: Optional[float]
    longitude: Optional[float]
    fuel_type: str
    driver_name: Optional[str] = "Unassigned"
    risk_reasons: List[str] = []
    recommended_action: str
    active_dtc_codes: List[str] = []
    recent_telemetry: List[Dict[str, Any]] = []

class FleetOverviewResponse(BaseModel):
    total_vehicles: int
    healthy_vehicles: int
    at_risk_vehicles: int
    critical_vehicles: int
    active_alerts: int
    realtime_tps: float
    average_health_score: float
    health_distribution: Dict[str, int]
    make_breakdown: Dict[str, int]
    health_trend_7d: List[Dict[str, Any]]

class AlertSchema(BaseModel):
    id: str
    vin: str
    vehicle_name: str
    severity: str
    reason: str
    dtc_code: Optional[str]
    recommended_action: str
    status: str
    created_at: str
    resolved_at: Optional[str]

class AnalyticsResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    risk_distribution: Dict[str, int]
    top_dtc_faults: List[Dict[str, Any]]
    health_vs_mileage: List[Dict[str, Any]]
    maintenance_patterns: Dict[str, int]
    model_performance: Dict[str, Any]

class SystemHealthResponse(BaseModel):
    status: str
    events_per_sec: float
    avg_processing_latency_ms: float
    p95_processing_latency_ms: float
    p99_processing_latency_ms: float
    kafka_consumer_lag: int
    api_p95_latency_ms: float
    error_rate_pct: float
    db_status: str
    redis_status: str
    mongo_status: str
    active_vehicles_simulated: int
    uptime_seconds: float

class WorkOrderCreate(BaseModel):
    vin: str
    priority: str = "HIGH"
    title: str
    description: str
    scheduled_date: str

class SimulatorConfig(BaseModel):
    tps: int = 50
    anomaly_rate_pct: float = 5.0
    burst_mode: bool = False
    inject_duplicates: bool = False
    inject_out_of_order: bool = False
