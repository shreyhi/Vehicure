from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any

from app.database.init_db import AsyncSessionLocal
from app.models.db_models import Vehicle, Fleet

router = APIRouter(prefix="/health", tags=["Vehicle Health"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/summary")
async def get_health_summary(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Returns vehicle health distribution metrics and risk rankings."""
    result = await db.execute(select(Vehicle.risk_level, Vehicle.health_score))
    rows = result.all()
    
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    scores = []
    
    for r_level, h_score in rows:
        counts[r_level] = counts.get(r_level, 0) + 1
        scores.append(h_score)
        
    avg_score = round(sum(scores) / max(1, len(scores)), 1)
    
    return {
        "average_health_score": avg_score,
        "risk_breakdown": counts,
        "critical_percent": round((counts["CRITICAL"] / max(1, len(scores))) * 100.0, 2),
        "at_risk_percent": round(((counts["HIGH"] + counts["MEDIUM"]) / max(1, len(scores))) * 100.0, 2)
    }

@router.get("/top-risk", response_model=List[Dict[str, Any]])
async def get_top_risk_vehicles(limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    """Returns top N vehicles with highest risk scores for preventive maintenance prioritization."""
    query = (
        select(Vehicle, Fleet.name.label("fleet_name"))
        .join(Fleet, Vehicle.fleet_id == Fleet.id)
        .order_by(desc(Vehicle.risk_score), Vehicle.health_score.asc())
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()

    output = []
    for v, f_name in rows:
        output.append({
            "vin": v.vin,
            "vehicle_name": f"{v.make} {v.model} ({v.year})",
            "fleet_name": f_name,
            "health_score": v.health_score,
            "risk_score": v.risk_score,
            "risk_level": v.risk_level,
            "failure_prob": v.failure_prob,
            "last_engine_temp": v.last_engine_temp,
            "last_battery_voltage": v.last_battery_voltage,
            "odometer_km": v.odometer_km,
            "last_seen": v.last_seen.strftime("%Y-%m-%d %H:%M:%S")
        })
    return output
