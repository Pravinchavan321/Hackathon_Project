"""LangGraph Multi-Agent Workflow Graph for AgentShield AI.
Connects Planner, Receipt, Validation, Execution agents and the Governance Gateway.
Supports deterministic pauses (interrupts) for human manager approval and state resumption.
"""
from typing import Dict, Any, Optional, Tuple
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from backend.app.orchestration.state import WorkflowState
from backend.app.orchestration.nodes import (
    plan_node,
    receipt_node,
    validation_node,
    preparation_node,
    governance_gate_node,
    block_node,
    approval_node,
    revalidation_node,
    execute_node,
)


def route_after_governance(state: WorkflowState) -> str:
    """Route workflow based on deterministic governance decision."""
    decision = state.get("governance_decision", "DENY")
    if decision == "ALLOW":
        return "execute"
    elif decision == "REQUIRE_APPROVAL":
        return "approval"
    else:
        return "block"


def route_after_revalidation(state: WorkflowState) -> str:
    """Route workflow after human approval revalidation."""
    if state.get("approval_ok") is True:
        return "execute"
    return "block"


def build_workflow_graph(checkpointer: Optional[Any] = None):
    """Constructs and compiles the StateGraph workflow."""
    if checkpointer is None:
        checkpointer = MemorySaver()

    builder = StateGraph(WorkflowState)

    # 1. Register Nodes
    builder.add_node("plan", plan_node)
    builder.add_node("receipt", receipt_node)
    builder.add_node("validation", validation_node)
    builder.add_node("preparation", preparation_node)
    builder.add_node("governance_gate", governance_gate_node)
    builder.add_node("approval", approval_node)
    builder.add_node("revalidation", revalidation_node)
    builder.add_node("block", block_node)
    builder.add_node("execute", execute_node)

    # 2. Sequential Agent Flow
    builder.add_edge(START, "plan")
    builder.add_edge("plan", "receipt")
    builder.add_edge("receipt", "validation")
    builder.add_edge("validation", "preparation")
    builder.add_edge("preparation", "governance_gate")

    # 3. Governance Conditional Routing
    builder.add_conditional_edges(
        "governance_gate",
        route_after_governance,
        {
            "execute": "execute",
            "approval": "approval",
            "block": "block",
        },
    )

    # 4. Human Approval Flow
    builder.add_edge("approval", "revalidation")
    builder.add_conditional_edges(
        "revalidation",
        route_after_revalidation,
        {
            "execute": "execute",
            "block": "block",
        },
    )

    # 5. Terminal Nodes
    builder.add_edge("execute", END)
    builder.add_edge("block", END)

    return builder.compile(checkpointer=checkpointer)


# Default shared in-memory workflow instance for execution
default_checkpointer = MemorySaver()
default_workflow = build_workflow_graph(checkpointer=default_checkpointer)


def run_workflow(
    task_id: str,
    user_id: str,
    user_role: str,
    input_text: str,
    input_data: Optional[Dict[str, Any]] = None,
    receipt_file_id: Optional[str] = None,
    workflow_app: Optional[Any] = None,
) -> Tuple[Dict[str, Any], bool]:
    """Runs a workflow to completion or until an approval interrupt is triggered.
    
    Returns:
        (final_or_paused_state, is_paused)
    """
    app = workflow_app or default_workflow
    config = {"configurable": {"thread_id": task_id}}

    initial_state: WorkflowState = {
        "task_id": task_id,
        "user_id": user_id,
        "user_role": user_role,
        "input_text": input_text,
        "input_data": input_data or {},
        "receipt_file_id": receipt_file_id,
        "agent_trace": [],
        "status": "QUEUED",
    }

    result = app.invoke(initial_state, config=config)
    
    # Inspect current state checkpoint
    current_snapshot = app.get_state(config)
    is_paused = bool(current_snapshot.next)  # True if paused at an interrupt node

    return result, is_paused


def resume_workflow(
    task_id: str,
    approval_verdict: Dict[str, Any],
    workflow_app: Optional[Any] = None,
) -> Dict[str, Any]:
    """Resumes a paused workflow checkpoint using a Command(resume=...) payload.
    
    Args:
        task_id: The thread_id identifying the paused execution.
        approval_verdict: e.g. {"verdict": "approved", "approver_id": "mgr1", "approval_id": "appr-..."}
    """
    app = workflow_app or default_workflow
    config = {"configurable": {"thread_id": task_id}}

    resume_cmd = Command(resume=approval_verdict)
    res = app.invoke(resume_cmd, config=config)
    return res
