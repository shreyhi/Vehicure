from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Dict, Any, List
import random
from datetime import datetime, timedelta

from app.database.init_db import AsyncSessionLocal
from app.models.db_models import Vehicle, Fleet, Alert, MaintenanceOrder
from app.services.rule_engine import RuleEngine
from app.services.ml_engine import ml_engine_singleton
from app.database.mongo_store import MongoStore
from app.config import settings

router = APIRouter(prefix="/vehicles", tags=["Vehicle Details"])
mongo_store = MongoStore(settings.MONGO_URL)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/{vin}", response_model=Dict[str, Any])
async def get_vehicle_details(vin: str, db: AsyncSession = Depends(get_db)):
    """Returns comprehensive vehicle profile, live/historical telemetry, risk explanations, and maintenance logs."""
    query = (
        select(Vehicle, Fleet.name.label("fleet_name"))
        .join(Fleet, Vehicle.fleet_id == Fleet.id)
        .where(Vehicle.vin == vin)
    )
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"Vehicle with VIN {vin} not found.")

    v, fleet_name = row

    # Generate synthetic telemetry payload for live rule & ML evaluation
    sample_telemetry = {
        "engine_temp": v.last_engine_temp,
        "battery_voltage": v.last_battery_voltage,
        "odometer_km": v.odometer_km,
        "speed_kmh": v.last_speed_kmh,
        "dtc_codes": ["P0301", "P0217"] if v.risk_level in ["HIGH", "CRITICAL"] else [],
        "harsh_braking": v.risk_level == "CRITICAL",
        "harsh_accel": False,
        "fuel_level_pct": 65.0
    }

    rule_penalty, risk_reasons, rec_action = RuleEngine.evaluate_telemetry_rules(sample_telemetry)
    ml_prob = ml_engine_singleton.predict_failure_probability(sample_telemetry)

    # 10 recent historical telemetry data points for charts
    history_charts = []
    base_time = datetime.utcnow()
    for i in range(12):
        t_stamp = (base_time - timedelta(minutes=(11 - i) * 5)).strftime("%H:%M")
        temp_noise = random.uniform(-1.5, 1.5)
        batt_noise = random.uniform(-0.05, 0.05)
        history_charts.append({
            "timestamp": t_stamp,
            "engine_temp": round(v.last_engine_temp + temp_noise, 1),
            "battery_voltage": round(v.last_battery_voltage + batt_noise, 2),
            "speed_kmh": round(max(0, v.last_speed_kmh + random.uniform(-10, 10)), 1)
        })

    # Fetch alerts for vehicle
    alerts_res = await db.execute(select(Alert).where(Alert.vin == vin).order_by(desc(Alert.created_at)))
    alerts = alerts_res.scalars().all()
    
    # Fetch maintenance orders
    maint_res = await db.execute(select(MaintenanceOrder).where(MaintenanceOrder.vin == vin).order_by(desc(MaintenanceOrder.created_at)))
    maint_orders = maint_res.scalars().all()

    return {
        "vin": v.vin,
        "make": v.make,
        "model": v.model,
        "year": v.year,
        "fuel_type": v.fuel_type,
        "fleet_name": fleet_name,
        "fleet_id": v.fleet_id,
        "odometer_km": v.odometer_km,
        "status": v.status,
        "health_score": v.health_score,
        "risk_score": v.risk_score,
        "risk_level": v.risk_level,
        "failure_prob": v.failure_prob if v.failure_prob > 0 else ml_prob,
        "current_state": {
            "latitude": v.last_latitude,
            "longitude": v.last_longitude,
            "speed_kmh": v.last_speed_kmh,
            "engine_temp": v.last_engine_temp,
            "battery_voltage": v.last_battery_voltage,
            "last_seen": v.last_seen.strftime("%Y-%m-%d %H:%M:%S")
        },
        "prediction_explanation": {
            "main_reasons": risk_reasons,
            "recommended_action": rec_action,
            "rule_risk_contribution": round(rule_penalty * 0.4, 1),
            "ml_risk_contribution": round(ml_prob * 0.6, 1)
        },
        "telemetry_history": history_charts,
        "active_alerts": [{
            "id": a.id,
            "severity": a.severity,
            "reason": a.reason,
            "dtc_code": a.dtc_code,
            "status": a.status,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for a in alerts],
        "maintenance_history": [{
            "id": m.id,
            "title": m.title,
            "priority": m.priority,
            "status": m.status,
            "scheduled_date": m.scheduled_date.strftime("%Y-%m-%d %H:%M:%S")
        } for m in maint_orders]
    }
