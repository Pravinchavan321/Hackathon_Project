"""Workflow State Definition for AgentShield AI.
Typed dictionary managing state across all LangGraph nodes and checkpoints.
"""
from typing import TypedDict, Optional, List, Dict, Any


class WorkflowState(TypedDict, total=False):
    """Shared typed state passed between LangGraph agent nodes."""

    # Task identity and principal context
    task_id: str
    user_id: str
    user_role: str

    # Input directives
    input_text: str
    input_data: Optional[Dict[str, Any]]
    receipt_file_id: Optional[str]

    # Agent step artifacts
    plan: Optional[Dict[str, Any]]
    receipt_data: Optional[Dict[str, Any]]
    validation_findings: Optional[Dict[str, Any]]
    proposed_action: Optional[Dict[str, Any]]

    # Governance decision and risk artifacts
    governance_decision: Optional[str]  # ALLOW | DENY | REQUIRE_APPROVAL
    governance_reasons: Optional[List[str]]
    risk_assessment: Optional[Dict[str, Any]]
    action_hash: Optional[str]

    # Human-in-the-loop approval artifacts
    approval_id: Optional[str]
    approval_payload: Optional[Dict[str, Any]]
    approval_ok: Optional[bool]

    # Tool execution results
    claim_id: Optional[str]
    execution_result: Optional[Dict[str, Any]]
    status: str  # QUEUED | RUNNING | SUCCEEDED | DENIED | WAITING_FOR_APPROVAL | FAILED
    error: Optional[str]

    # Observability trace
    current_agent: Optional[str]
    agent_trace: Optional[List[Dict[str, Any]]]
