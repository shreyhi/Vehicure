import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from app.services.simulator import simulator_singleton

router = APIRouter(prefix="/monitoring", tags=["Live Monitoring"])

@router.get("/recent")
async def get_recent_events(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns the most recent vehicle telemetry events from the live buffer."""
    buffer = simulator_singleton.recent_events_buffer
    return list(reversed(buffer))[:limit]

@router.get("/stream")
async def stream_telemetry_events():
    """SSE (Server-Sent Events) endpoint for real-time live vehicle event stream."""
    async def event_generator():
        last_sent_index = 0
        while True:
            buffer = simulator_singleton.recent_events_buffer
            if len(buffer) > last_sent_index:
                new_events = buffer[last_sent_index:]
                last_sent_index = len(buffer)
                for event in new_events:
                    yield f"data: {json.dumps(event)}\n\n"
            else:
                # Keep alive heartbeats
                yield f": heartbeat\n\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.websocket("/ws")
async def websocket_telemetry_stream(websocket: WebSocket):
    """WebSocket endpoint for bi-directional live telemetry monitoring."""
    await websocket.accept()
    last_sent_len = 0
    try:
        while True:
            buffer = simulator_singleton.recent_events_buffer
            if len(buffer) > last_sent_len:
                new_events = buffer[last_sent_len:]
                last_sent_len = len(buffer)
                for event in new_events:
                    await websocket.send_json(event)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
