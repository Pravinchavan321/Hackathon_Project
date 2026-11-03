"""Integration tests for Phase 9: WebSocket Task Streaming.
Tests client connection handshake, ping-pong messaging, and broadcast event streaming.
"""
import pytest
import asyncio
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.api.ws_routes import ws_manager


def test_websocket_connection_and_handshake():
    """Client connects to /ws/tasks/{task_id} and receives connection acknowledgement."""
    client = TestClient(app)
    task_id = "tsk-test-ws-001"

    with client.websocket_connect(f"/ws/tasks/{task_id}") as websocket:
        # First message is connection confirmation
        data = websocket.receive_json()
        assert data["event"] == "connected"
        assert data["task_id"] == task_id
        assert "Subscribed to live events" in data["payload"]["message"]


def test_websocket_ping_pong():
    """Client can send ping and receives pong response."""
    client = TestClient(app)
    task_id = "tsk-test-ws-002"

    with client.websocket_connect(f"/ws/tasks/{task_id}") as websocket:
        _ = websocket.receive_json()  # Handshake
        websocket.send_text("ping")
        resp = websocket.receive_json()
        assert resp["event"] == "pong"
        assert "timestamp" in resp


def test_websocket_manager_broadcast_event():
    """Manager broadcasts an agent step event to connected subscribers."""
    client = TestClient(app)
    task_id = "tsk-test-ws-003"

    with client.websocket_connect(f"/ws/tasks/{task_id}") as websocket:
        _ = websocket.receive_json()  # Handshake

        # Broadcast custom agent step event
        step_payload = {
            "agent": "PlannerAgent",
            "action": "deconstruct_request",
            "subtasks_count": 3,
        }
        asyncio.run(ws_manager.broadcast_task_event(task_id, "agent_step", step_payload))

        received = websocket.receive_json()
        assert received["event"] == "agent_step"
        assert received["task_id"] == task_id
        assert received["payload"]["agent"] == "PlannerAgent"
