from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime

from app.database.init_db import AsyncSessionLocal
from app.models.db_models import Alert, Vehicle, MaintenanceOrder
from app.models.schemas import AlertSchema, WorkOrderCreate
from app.services.alert_engine import AlertEngine

router = APIRouter(prefix="/alerts", tags=["Alerts Management"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("", response_model=List[AlertSchema])
async def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = "ACTIVE",
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Returns active/resolved fleet alerts with filters."""
    query = select(Alert, Vehicle.make, Vehicle.model).join(Vehicle, Alert.vin == Vehicle.vin)
    
    if severity and severity.upper() != "ALL":
        query = query.where(Alert.severity == severity.upper())
    if status and status.upper() != "ALL":
        query = query.where(Alert.status == status.upper())

    query = query.order_by(desc(Alert.created_at)).limit(limit)
    result = await db.execute(query)
    rows = result.all()

    alerts_list = []
    for alert, make, model in rows:
        alerts_list.append(AlertSchema(
            id=alert.id,
            vin=alert.vin,
            vehicle_name=f"{make} {model}",
            severity=alert.severity,
            reason=alert.reason,
            dtc_code=alert.dtc_code,
            recommended_action=alert.recommended_action,
            status=alert.status,
            created_at=alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            resolved_at=alert.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if alert.resolved_at else None
        ))
    return alerts_list

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    """Resolves an active alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = "RESOLVED"
    alert.resolved_at = datetime.utcnow()
    await db.commit()
    return {"message": f"Alert {alert_id} resolved successfully."}

@router.post("/{alert_id}/create-work-order")
async def trigger_work_order_from_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    """Triggers an automated preventive maintenance work order directly from an active alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    wo_data = AlertEngine.create_preventive_work_order(
        vin=alert.vin,
        alert_reason=alert.reason,
        recommended_action=alert.recommended_action
    )

    wo = MaintenanceOrder(
        id=wo_data["id"],
        vin=wo_data["vin"],
        priority=wo_data["priority"],
        title=wo_data["title"],
        description=wo_data["description"],
        status=wo_data["status"],
        scheduled_date=datetime.strptime(wo_data["scheduled_date"], "%Y-%m-%d %H:%M:%S"),
        created_at=datetime.utcnow()
    )
    db.add(wo)
    alert.status = "ACKNOWLEDGED"
    await db.commit()

    return {"message": "Preventive maintenance work order created", "work_order": wo_data}
