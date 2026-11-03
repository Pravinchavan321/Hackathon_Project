"""WebSocket Streaming Routes and Connection Manager for AgentShield AI.
Provides real-time event streaming for agent steps, governance evaluations,
and human approval interrupts.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class TaskConnectionManager:
    """Manages active WebSocket connections per task ID for live event streaming."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)

    def disconnect(self, task_id: str, websocket: WebSocket):
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast_task_event(self, task_id: str, event_type: str, payload: Dict[str, Any]):
        """Broadcasts an event message to all connected clients for the task."""
        if task_id not in self.active_connections:
            return

        message = {
            "task_id": task_id,
            "event": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }

        dead_connections = []
        for connection in self.active_connections[task_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(task_id, dead)


ws_manager = TaskConnectionManager()


@router.websocket("/ws/tasks/{task_id}")
async def task_websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket streaming endpoint for real-time task lifecycle events."""
    await ws_manager.connect(task_id, websocket)
    try:
        # Send initial handshake event
        await websocket.send_json({
            "task_id": task_id,
            "event": "connected",
            "payload": {"message": f"Subscribed to live events for task {task_id}"},
            "timestamp": datetime.utcnow().isoformat(),
        })

        while True:
            # Keep connection alive; process client pings or control messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"event": "pong", "timestamp": datetime.utcnow().isoformat()})
    except WebSocketDisconnect:
        ws_manager.disconnect(task_id, websocket)
    except Exception:
        ws_manager.disconnect(task_id, websocket)
