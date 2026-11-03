"""LangGraph Node Implementations for AgentShield AI.
Each node is restart-safe and updates the shared WorkflowState.
"""
from typing import Dict, Any
from langgraph.types import interrupt
from backend.app.orchestration.state import WorkflowState
from backend.app.agents.planner_agent import PlannerAgent
from backend.app.agents.receipt_agent import ReceiptAgent
from backend.app.agents.validation_agent import ValidationAgent
from backend.app.agents.execution_agent import ExecutionAgent
from backend.app.governance.governance_gateway import GovernanceGateway
from backend.app.tools.claim_executor import ClaimExecutor

# Instantiated services
planner = PlannerAgent()
receipt_extractor = ReceiptAgent()
validator = ValidationAgent()
executor = ExecutionAgent()
gateway = GovernanceGateway()
claim_tool = ClaimExecutor()


def plan_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 1: Planner Agent decomposes request."""
    plan = planner.generate_plan(state.get("input_text", ""))
    trace = list(state.get("agent_trace") or [])
    trace.append({"agent": "PlannerAgent", "action": "planned", "subtasks_count": len(plan.get("subtasks", []))})
    return {"plan": plan, "current_agent": "ReceiptAgent", "agent_trace": trace, "status": "RUNNING"}


def receipt_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 2: Receipt Agent processes invoice input."""
    raw_input = state.get("input_text", "")
    claim_in = state.get("input_data") or {}
    text_to_parse = f"{raw_input} {claim_in.get('description', '')} {claim_in.get('category', '')}"

    receipt_data = receipt_extractor.process_receipt(text_to_parse)
    trace = list(state.get("agent_trace") or [])
    trace.append({"agent": "ReceiptAgent", "action": "extracted", "merchant": receipt_data.get("merchant")})
    return {"receipt_data": receipt_data, "current_agent": "ValidationAgent", "agent_trace": trace}


def validation_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 3: Validation Agent checks consistency and duplicates."""
    claim_in = state.get("input_data") or {}
    receipt_data = state.get("receipt_data") or {}
    user_id = state.get("user_id", "emp1")

    validation = validator.validate(
        claim_data=claim_in,
        receipt_data=receipt_data,
        user_id=user_id,
        receipt_hash=state.get("receipt_file_id"),
    )
    trace = list(state.get("agent_trace") or [])
    trace.append({"agent": "ValidationAgent", "action": "validated", "is_valid": validation.get("is_valid")})
    return {"validation_findings": validation, "current_agent": "ExecutionAgent", "agent_trace": trace}


def preparation_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 4: Execution Agent formats proposed action (PROPOSAL ONLY)."""
    claim_in = state.get("input_data") or {}
    receipt_data = state.get("receipt_data") or {}
    user_id = state.get("user_id", "emp1")
    note = claim_in.get("note") or state.get("input_text", "")

    proposal = executor.prepare_proposal(
        claim_data=claim_in,
        receipt_data=receipt_data,
        user_id=user_id,
        note=note,
    )
    trace = list(state.get("agent_trace") or [])
    trace.append({"agent": "ExecutionAgent", "action": "proposed", "tool": proposal.get("tool")})
    return {"proposed_action": proposal, "current_agent": "GovernanceGateway", "agent_trace": trace}


def governance_gate_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 5: Governance Gateway evaluates policies, permissions, and risk."""
    proposal = state.get("proposed_action") or {}
    context = {
        "user_id": state.get("user_id", "emp1"),
        "user_role": state.get("user_role", "EMPLOYEE"),
        "task_id": state.get("task_id", "t-default"),
    }

    gov_res = gateway.evaluate(
        proposed_action=proposal,
        context=context,
    )

    trace = list(state.get("agent_trace") or [])
    trace.append({
        "agent": "GovernanceGateway",
        "action": "evaluated",
        "decision": gov_res.get("decision"),
        "reasons": gov_res.get("reasons"),
    })

    return {
        "governance_decision": gov_res.get("decision"),
        "governance_reasons": gov_res.get("reasons", []),
        "risk_assessment": gov_res.get("risk"),
        "action_hash": gov_res.get("action_hash"),
        "approval_id": gov_res.get("approval_id"),
        "agent_trace": trace,
    }


def block_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 6: Handles DENY decision safely without executing side-effects."""
    trace = list(state.get("agent_trace") or [])
    trace.append({"agent": "GovernanceGateway", "action": "blocked", "reasons": state.get("governance_reasons")})
    existing_error = state.get("error")
    error_msg = existing_error if existing_error else f"Operation denied by policy governance: {state.get('governance_reasons')}"
    return {
        "status": "DENIED",
        "error": error_msg,
        "agent_trace": trace,
    }


def approval_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 7: Pauses the LangGraph execution using interrupt().
    Checkpoints state and waits for human manager sign-off.
    """
    trace = list(state.get("agent_trace") or [])
    trace.append({"agent": "ApprovalManager", "action": "paused_for_approval", "approval_id": state.get("approval_id")})

    # The graph pauses execution right here until resumed with Command(resume=...)
    approval_verdict = interrupt({
        "task_id": state.get("task_id"),
        "approval_id": state.get("approval_id"),
        "action_hash": state.get("action_hash"),
        "proposed_action": state.get("proposed_action"),
        "reasons": state.get("governance_reasons"),
        "risk_assessment": state.get("risk_assessment"),
    })

    return {"approval_payload": approval_verdict, "agent_trace": trace, "status": "RUNNING"}


def revalidation_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 8: Re-evaluates exact action hash and policy upon resume."""
    appr_payload = state.get("approval_payload") or {}
    verdict = appr_payload.get("verdict")
    approval_id = appr_payload.get("approval_id") or state.get("approval_id")
    proposal = state.get("proposed_action") or {}

    trace = list(state.get("agent_trace") or [])

    if verdict != "approved":
        trace.append({"agent": "GovernanceGateway", "action": "revalidation_rejected", "verdict": verdict})
        return {"status": "DENIED", "approval_ok": False, "error": "Manager rejected proposed action", "agent_trace": trace}

    # Re-evaluate with approval ticket
    context = {
        "user_id": state.get("user_id", "emp1"),
        "user_role": state.get("user_role", "EMPLOYEE"),
        "task_id": state.get("task_id", "t-default"),
    }

    fresh_res = gateway.evaluate(
        proposed_action=proposal,
        context=context,
        approval_id=approval_id,
    )

    if fresh_res.get("decision") != "ALLOW":
        trace.append({"agent": "GovernanceGateway", "action": "revalidation_failed", "reasons": fresh_res.get("reasons")})
        return {"status": "DENIED", "approval_ok": False, "error": f"Revalidation failed: {fresh_res.get('reasons')}", "agent_trace": trace}

    trace.append({"agent": "GovernanceGateway", "action": "revalidation_passed", "decision": "ALLOW"})
    return {"status": "RUNNING", "approval_ok": True, "agent_trace": trace}


def execute_node(state: WorkflowState) -> Dict[str, Any]:
    """Node 9: Controlled Tool Execution. ONLY invoked when ALLOW decision is verified."""
    proposal = state.get("proposed_action") or {}
    user_id = state.get("user_id", "emp1")
    task_id = state.get("task_id", "t-default")

    ticket = {
        "decision": "ALLOW",
        "action_hash": state.get("action_hash"),
    }

    try:
        exec_res = claim_tool.execute_claim_submission(
            proposed_action=proposal,
            user_id=user_id,
            task_id=task_id,
            governance_ticket=ticket,
            idempotency_key=f"idem-{task_id}",
            approved_by=(state.get("approval_payload") or {}).get("approver_id", "SystemAuto"),
        )
        trace = list(state.get("agent_trace") or [])
        trace.append({"agent": "ClaimExecutor", "action": "executed", "claim_id": exec_res.get("claim_id")})
        return {
            "status": "SUCCEEDED",
            "execution_result": exec_res,
            "claim_id": exec_res.get("claim_id"),
            "agent_trace": trace,
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}
