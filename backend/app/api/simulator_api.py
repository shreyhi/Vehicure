import asyncio
from fastapi import APIRouter
from typing import Dict, Any
from app.services.simulator import simulator_singleton
from app.models.schemas import SimulatorConfig

router = APIRouter(prefix="/simulator", tags=["Vehicle Simulator Control"])

@router.get("/status")
async def get_simulator_status() -> Dict[str, Any]:
    """Returns simulator current status, target TPS, and injection modes."""
    return {
        "is_running": simulator_singleton.is_running,
        "num_vehicles": simulator_singleton.num_vehicles,
        "target_tps": simulator_singleton.tps,
        "anomaly_rate_pct": simulator_singleton.anomaly_rate_pct,
        "burst_mode": simulator_singleton.burst_mode,
        "inject_duplicates": simulator_singleton.inject_duplicates,
        "inject_out_of_order": simulator_singleton.inject_out_of_order,
        "buffered_events_count": len(simulator_singleton.recent_events_buffer)
    }

@router.post("/start")
async def start_simulator():
    """Starts the real-time telemetry streaming loop in the background."""
    if not simulator_singleton.is_running:
        asyncio.create_task(simulator_singleton.start_streaming())
        return {"message": "Vehicle simulator started successfully."}
    return {"message": "Simulator is already running."}

@router.post("/stop")
async def stop_simulator():
    """Stops the real-time telemetry streaming loop."""
    simulator_singleton.stop_streaming()
    return {"message": "Vehicle simulator stopped."}

@router.post("/config")
async def update_simulator_config(config: SimulatorConfig):
    """Updates simulator Target TPS rate, anomaly percentage, and injection parameters."""
    simulator_singleton.tps = config.tps
    simulator_singleton.anomaly_rate_pct = config.anomaly_rate_pct
    simulator_singleton.burst_mode = config.burst_mode
    simulator_singleton.inject_duplicates = config.inject_duplicates
    simulator_singleton.inject_out_of_order = config.inject_out_of_order
    return {"message": "Simulator configuration updated", "config": config.dict()}

@router.post("/inject-fault")
async def inject_fault_anomaly(vin: str, dtc_code: str = "P0217"):
    """Manually injects an immediate critical fault anomaly into a specific vehicle."""
    for v in simulator_singleton.vehicles:
        if v["vin"] == vin:
            v["has_active_fault"] = True
            v["engine_temp"] = 118.5
            v["battery_voltage"] = 10.8
            return {"message": f"Critical fault anomaly injected into vehicle {vin}"}
    return {"message": f"Vehicle {vin} updated with fault trigger"}
