"""Task Execution and Orchestration API Routes for AgentShield AI.
Provides endpoints to trigger multi-agent task execution, inspect execution traces,
and resume workflows paused at human approval checkpoints.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.middleware.auth_middleware import get_current_user
from backend.app.models.task import TaskCreate
from backend.app.orchestration.graph import run_workflow, resume_workflow
from backend.app.governance.approval_manager import ApprovalManager
from backend.app.database.mongodb import mongo_manager
from backend.app.database import collections

router = APIRouter()
approval_manager = ApprovalManager()

# In-memory storage for offline / testing mode
_MEMORY_TASKS: Dict[str, Dict[str, Any]] = {}


class TaskResumeRequest(BaseModel):
    approval_id: str = Field(..., description="The ID of the approved ticket")
    verdict: str = Field(default="approved", description="Decision: 'approved' or 'rejected'")


@router.post("/run", tags=["Tasks"])
async def run_agent_task(
    request: TaskCreate,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Initiates an autonomous Multi-Agent task workflow.
    Executes through Planner -> Receipt -> Validation -> Execution -> Governance Gateway.
    If governance requires manager sign-off, halts execution with WAITING_FOR_APPROVAL status.
    """
    task_id = "tsk-" + uuid.uuid4().hex[:8]
    user_id = current_user.get("user_id", "u-anon")
    user_role = current_user.get("role", "EMPLOYEE")

    result, is_paused = run_workflow(
        task_id=task_id,
        user_id=user_id,
        user_role=user_role,
        input_text=request.input_text,
        input_data=request.claim_data,
        receipt_file_id=request.receipt_file_id,
    )

    final_status = "WAITING_FOR_APPROVAL" if is_paused else result.get("status", "SUCCEEDED")
    now = datetime.utcnow()

    task_record = {
        "task_id": task_id,
        "requester_id": user_id,
        "input_text": request.input_text,
        "status": final_status,
        "plan": result.get("plan"),
        "receipt_data": result.get("receipt_data"),
        "validation_findings": result.get("validation_findings"),
        "proposed_action": result.get("proposed_action"),
        "governance_decision": result.get("governance_decision"),
        "governance_reasons": result.get("governance_reasons", []),
        "risk_assessment": result.get("risk_assessment"),
        "action_hash": result.get("action_hash"),
        "approval_id": result.get("approval_id"),
        "execution_result": result.get("execution_result"),
        "claim_id": result.get("claim_id"),
        "error": result.get("error"),
        "agent_trace": result.get("agent_trace", []),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    _MEMORY_TASKS[task_id] = task_record

    db = mongo_manager.get_db()
    if db is not None:
        db[collections.AGENT_TASKS].insert_one({**task_record, "created_at": now, "updated_at": now})

    return task_record


@router.post("/{task_id}/resume", tags=["Tasks"])
async def resume_agent_task(
    task_id: str,
    request: TaskResumeRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Resumes a checkpointed workflow paused at a human approval interrupt.
    Verifies human manager verdict and revalidates exact action hash before gated tool execution.
    """
    existing = _MEMORY_TASKS.get(task_id)
    if not existing:
        db = mongo_manager.get_db()
        if db is not None:
            existing = db[collections.AGENT_TASKS].find_one({"task_id": task_id})

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    # Resume the LangGraph workflow checkpoint
    approval_verdict = {
        "verdict": request.verdict,
        "approver_id": current_user.get("user_id"),
        "approval_id": request.approval_id,
    }

    resumed_result = resume_workflow(
        task_id=task_id,
        approval_verdict=approval_verdict,
    )

    now = datetime.utcnow()
    updated_record = {
        **existing,
        "status": resumed_result.get("status", "SUCCEEDED"),
        "claim_id": resumed_result.get("claim_id") or existing.get("claim_id"),
        "execution_result": resumed_result.get("execution_result"),
        "agent_trace": resumed_result.get("agent_trace", existing.get("agent_trace", [])),
        "error": resumed_result.get("error"),
        "updated_at": now.isoformat(),
    }

    _MEMORY_TASKS[task_id] = updated_record
    db = mongo_manager.get_db()
    if db is not None:
        db[collections.AGENT_TASKS].update_one(
            {"task_id": task_id},
            {"$set": {**updated_record, "updated_at": now}},
        )

    return updated_record


@router.get("/{task_id}", tags=["Tasks"])
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Retrieve execution status and agent traces for a task."""
    record = _MEMORY_TASKS.get(task_id)
    if not record:
        db = mongo_manager.get_db()
        if db is not None:
            record = db[collections.AGENT_TASKS].find_one({"task_id": task_id})

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    return record
