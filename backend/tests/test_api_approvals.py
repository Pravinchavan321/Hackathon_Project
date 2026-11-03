"""Integration tests for Phase 7: Human Approval & State Pause/Resume REST API.
Verifies task initiation, approval pause, pending queue, self-approval prevention,
manager sign-off, and durable workflow resumption.
"""
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.governance.approval_manager import _MEMORY_APPROVALS, _CONSUMED_APPROVALS
from backend.app.api.task_routes import _MEMORY_TASKS
from backend.app.services.auth_service import create_access_token


@pytest.fixture(autouse=True)
def reset_in_memory_state():
    """Clear memory storage before each test."""
    _MEMORY_APPROVALS.clear()
    _CONSUMED_APPROVALS.clear()
    _MEMORY_TASKS.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def employee_headers():
    token = create_access_token({"sub": "emp-charlie", "email": "charlie@agentshield.ai", "role": "EMPLOYEE"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def manager_headers():
    token = create_access_token({"sub": "mgr-dana", "email": "dana@agentshield.ai", "role": "MANAGER"})
    return {"Authorization": f"Bearer {token}"}


def test_api_task_under_threshold_completes_without_pause(client, employee_headers):
    """Compliant expense <= ₹5,000 runs to SUCCEEDED immediately via REST API."""
    payload = {
        "input_text": "Taxi fare reimbursement Rs 2200 for client presentation",
        "claim_data": {
            "amount": 2200.0,
            "category": "travel",
            "description": "Taxi fare for client presentation",
            "merchant": "Uber",
            "receipt_id": "rec-uber-2200",
        },
        "receipt_file_id": "rec-uber-2200",
    }

    res = client.post("/api/v1/tasks/run", json=payload, headers=employee_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCEEDED"
    assert data["claim_id"] is not None
    assert data["claim_id"].startswith("clm-")
    assert data["approval_id"] is None


def test_api_high_value_task_pauses_and_resumes_after_manager_approval(client, employee_headers, manager_headers):
    """High-value expense (> ₹5,000) halts at WAITING_FOR_APPROVAL, gets approved, and resumes to SUCCEEDED."""
    # 1. Employee initiates high-value reimbursement
    payload = {
        "input_text": "Round-trip flight booking to Delhi office for Rs 14500",
        "claim_data": {
            "amount": 14500.0,
            "category": "travel",
            "description": "Flight booking to Delhi office",
            "merchant": "Air India",
            "receipt_id": "rec-flight-14500",
        },
        "receipt_file_id": "rec-flight-14500",
    }

    run_res = client.post("/api/v1/tasks/run", json=payload, headers=employee_headers)
    assert run_res.status_code == 200
    task_data = run_res.json()

    assert task_data["status"] == "WAITING_FOR_APPROVAL"
    task_id = task_data["task_id"]
    approval_id = task_data["approval_id"]
    assert approval_id is not None
    assert approval_id.startswith("appr-")

    # 2. Employee cannot list pending manager approvals (403 Forbidden)
    emp_pending = client.get("/api/v1/approvals/pending", headers=employee_headers)
    assert emp_pending.status_code == 403

    # 3. Manager queries pending approvals (200 OK)
    mgr_pending = client.get("/api/v1/approvals/pending", headers=manager_headers)
    assert mgr_pending.status_code == 200
    items = mgr_pending.json()
    assert len(items) >= 1
    found = [i for i in items if i["approval_id"] == approval_id]
    assert len(found) == 1
    assert found[0]["action_hash"] == task_data["action_hash"]

    # 4. Requester CANNOT self-approve (Strict 403 Forbidden)
    self_appr = client.post(
        f"/api/v1/approvals/{approval_id}/decide",
        json={"verdict": "approved", "reason": "Self sign-off"},
        headers=employee_headers,
    )
    # Employee role cannot even access decide endpoint (needs MANAGER/ADMIN)
    assert self_appr.status_code == 403

    # 5. Manager approves the ticket
    decide_res = client.post(
        f"/api/v1/approvals/{approval_id}/decide",
        json={"verdict": "approved", "reason": "Approved business travel to Delhi"},
        headers=manager_headers,
    )
    assert decide_res.status_code == 200
    assert decide_res.json()["status"] == "APPROVED"

    # 6. Resume the paused workflow via REST API
    resume_res = client.post(
        f"/api/v1/tasks/{task_id}/resume",
        json={"approval_id": approval_id, "verdict": "approved"},
        headers=manager_headers,
    )
    assert resume_res.status_code == 200
    resumed_data = resume_res.json()
    assert resumed_data["status"] == "SUCCEEDED"
    assert resumed_data["claim_id"] is not None
    assert resumed_data["claim_id"].startswith("clm-")

    # 7. Check task status via GET endpoint
    get_res = client.get(f"/api/v1/tasks/{task_id}", headers=employee_headers)
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "SUCCEEDED"


def test_api_high_value_task_denied_on_manager_rejection(client, employee_headers, manager_headers):
    """High-value expense paused for approval terminates in DENIED when manager rejects."""
    payload = {
        "input_text": "Executive team dinner luxury buffet Rs 18000",
        "claim_data": {
            "amount": 18000.0,
            "category": "meals",
            "description": "Executive dinner buffet",
            "merchant": "Luxury Palace",
            "receipt_id": "rec-dinner-18000",
        },
        "receipt_file_id": "rec-dinner-18000",
    }

    run_res = client.post("/api/v1/tasks/run", json=payload, headers=employee_headers)
    assert run_res.status_code == 200
    task_data = run_res.json()
    task_id = task_data["task_id"]
    approval_id = task_data["approval_id"]

    # Manager rejects
    decide_res = client.post(
        f"/api/v1/approvals/{approval_id}/decide",
        json={"verdict": "rejected", "reason": "Meal expense exceeds per-head policy limit"},
        headers=manager_headers,
    )
    assert decide_res.status_code == 200
    assert decide_res.json()["status"] == "REJECTED"

    # Resume with rejection
    resume_res = client.post(
        f"/api/v1/tasks/{task_id}/resume",
        json={"approval_id": approval_id, "verdict": "rejected"},
        headers=manager_headers,
    )
    assert resume_res.status_code == 200
    resumed_data = resume_res.json()
    assert resumed_data["status"] == "DENIED"
    assert resumed_data["claim_id"] is None
