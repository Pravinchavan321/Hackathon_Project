"""Unit and Integration Tests for Phase 6 Multi-Agent System (LangGraph).
Tests agent orchestration, governance gating, interrupt on approval, and resumption.
"""
import uuid
import pytest
from backend.app.orchestration.graph import (
    build_workflow_graph,
    run_workflow,
    resume_workflow,
)
from backend.app.governance.approval_manager import (
    ApprovalManager,
    _MEMORY_APPROVALS,
    _CONSUMED_APPROVALS,
)
from backend.app.governance.governance_gateway import GovernanceGateway


@pytest.fixture(autouse=True)
def reset_globals():
    """Clear approvals and audit state between tests."""
    _MEMORY_APPROVALS.clear()
    _CONSUMED_APPROVALS.clear()


def test_compliant_expense_under_threshold_executes_successfully():
    """Task <= ₹5,000 in valid category flows through all agents and executes."""
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    input_text = "Please process my taxi travel reimbursement of Rs 3500 for client site visit"
    input_data = {
        "amount": 3500.0,
        "category": "travel",
        "description": "Taxi travel reimbursement",
        "merchant": "Uber India",
        "receipt_id": "rec-12345",
    }

    result, is_paused = run_workflow(
        task_id=task_id,
        user_id="emp_001",
        user_role="EMPLOYEE",
        input_text=input_text,
        input_data=input_data,
        receipt_file_id="rec-12345",
    )

    assert not is_paused
    assert result.get("status") == "SUCCEEDED"
    assert result.get("governance_decision") == "ALLOW"
    assert "claim_id" in result
    assert result.get("claim_id").startswith("clm-")

    # Verify complete agent trace
    trace = result.get("agent_trace", [])
    agent_names = [t.get("agent") for t in trace]
    assert "PlannerAgent" in agent_names
    assert "ReceiptAgent" in agent_names
    assert "ValidationAgent" in agent_names
    assert "ExecutionAgent" in agent_names
    assert "GovernanceGateway" in agent_names
    assert "ClaimExecutor" in agent_names


def test_banned_category_is_blocked_by_governance():
    """Policy violation (e.g. gambling/alcohol) is blocked without executing."""
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    input_text = "Submit reimbursement for casino gambling chips Rs 4000"
    input_data = {
        "amount": 4000.0,
        "category": "gambling",
        "description": "Casino chips",
        "merchant": "Casino Goa",
        "receipt_id": "rec-gambling",
    }

    result, is_paused = run_workflow(
        task_id=task_id,
        user_id="emp_002",
        user_role="EMPLOYEE",
        input_text=input_text,
        input_data=input_data,
        receipt_file_id="rec-gambling",
    )

    assert not is_paused
    assert result.get("status") == "DENIED"
    assert result.get("governance_decision") == "DENY"
    assert "claim_id" not in result
    assert "denied by policy" in result.get("error", "").lower()


def test_high_value_expense_pauses_for_approval_and_resumes_upon_signoff():
    """Task > ₹5,000 pauses execution at approval node, then resumes after manager sign-off."""
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    input_text = "Submit flight reimbursement to Bangalore conference for Rs 12000"
    input_data = {
        "amount": 12000.0,
        "category": "travel",
        "description": "Flight to Bangalore conference",
        "merchant": "Air India",
        "receipt_id": "rec-flight-12000",
    }

    # Step 1: Run workflow — should pause at approval node
    paused_state, is_paused = run_workflow(
        task_id=task_id,
        user_id="emp_003",
        user_role="EMPLOYEE",
        input_text=input_text,
        input_data=input_data,
        receipt_file_id="rec-flight-12000",
    )

    assert is_paused is True
    assert paused_state.get("governance_decision") == "REQUIRE_APPROVAL"
    approval_id = paused_state.get("approval_id")
    assert approval_id is not None
    assert approval_id.startswith("appr-")

    # Step 2: Manager reviews and approves the pending ticket
    mgr = ApprovalManager()
    ok, status = mgr.record_decision(
        approval_id=approval_id,
        approver_id="mgr_alice",
        approver_role="MANAGER",
        verdict="approved",
        reason="Approved for annual tech conference",
    )
    assert ok is True
    assert status == "APPROVED"

    # Step 3: Resume workflow
    resumed_result = resume_workflow(
        task_id=task_id,
        approval_verdict={
            "verdict": "approved",
            "approver_id": "mgr_alice",
            "approval_id": approval_id,
        },
    )

    assert resumed_result.get("status") == "SUCCEEDED"
    assert "claim_id" in resumed_result
    assert resumed_result.get("claim_id").startswith("clm-")

    # Verify trace contains approval and revalidation
    trace = resumed_result.get("agent_trace", [])
    actions = [t.get("action") for t in trace]
    assert "paused_for_approval" in actions
    assert "revalidation_passed" in actions
    assert "executed" in actions


def test_high_value_expense_denied_when_manager_rejects():
    """Task > ₹5,000 paused for approval terminates in DENIED when manager rejects."""
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    input_text = "Submit luxury suite lodging for Rs 25000"
    input_data = {
        "amount": 25000.0,
        "category": "lodging",
        "description": "Luxury suite",
        "merchant": "Grand Palace Hotel",
        "receipt_id": "rec-hotel-25000",
    }

    paused_state, is_paused = run_workflow(
        task_id=task_id,
        user_id="emp_004",
        user_role="EMPLOYEE",
        input_text=input_text,
        input_data=input_data,
        receipt_file_id="rec-hotel-25000",
    )

    assert is_paused is True
    approval_id = paused_state.get("approval_id")

    # Manager rejects
    mgr = ApprovalManager()
    ok, status = mgr.record_decision(
        approval_id=approval_id,
        approver_id="mgr_bob",
        approver_role="MANAGER",
        verdict="rejected",
        reason="Out of policy lodging limits",
    )
    assert ok is True
    assert status == "REJECTED"

    # Resume with rejection verdict
    resumed_result = resume_workflow(
        task_id=task_id,
        approval_verdict={
            "verdict": "rejected",
            "approver_id": "mgr_bob",
            "approval_id": approval_id,
        },
    )

    assert resumed_result.get("status") == "DENIED"
    assert "rejected" in resumed_result.get("error", "").lower()
    assert "claim_id" not in resumed_result
