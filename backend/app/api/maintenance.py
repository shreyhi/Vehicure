from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.database.init_db import AsyncSessionLocal
from app.models.db_models import MaintenanceOrder, Vehicle
from app.models.schemas import WorkOrderCreate

router = APIRouter(prefix="/maintenance", tags=["Preventive Maintenance"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("", response_model=List[Dict[str, Any]])
async def get_work_orders(db: AsyncSession = Depends(get_db)):
    """Returns preventive maintenance work orders list."""
    query = (
        select(MaintenanceOrder, Vehicle.make, Vehicle.model)
        .join(Vehicle, MaintenanceOrder.vin == Vehicle.vin)
        .order_by(desc(MaintenanceOrder.created_at))
    )
    result = await db.execute(query)
    rows = result.all()

    orders = []
    for m, make, model in rows:
        orders.append({
            "id": m.id,
            "vin": m.vin,
            "vehicle_name": f"{make} {model}",
            "title": m.title,
            "description": m.description,
            "priority": m.priority,
            "status": m.status,
            "scheduled_date": m.scheduled_date.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return orders

@router.post("", response_model=Dict[str, Any])
async def create_work_order(data: WorkOrderCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new preventive maintenance work order."""
    wo_id = f"WO-{uuid.uuid4().hex[:8].upper()}"
    try:
        sched_dt = datetime.strptime(data.scheduled_date, "%Y-%m-%d %H:%M:%S")
    except Exception:
        sched_dt = datetime.utcnow()

    wo = MaintenanceOrder(
        id=wo_id,
        vin=data.vin,
        priority=data.priority,
        title=data.title,
        description=data.description,
        status="SCHEDULED",
        scheduled_date=sched_dt,
        created_at=datetime.utcnow()
    )
    db.add(wo)
    await db.commit()
    return {"message": "Work order created successfully", "id": wo_id}
