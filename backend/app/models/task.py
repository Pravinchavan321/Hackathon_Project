"""Agent Task models and schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    DENIED = "DENIED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class TaskCreate(BaseModel):
    input_text: str = Field(..., min_length=3, description="Natural language prompt")
    claim_data: Optional[Dict[str, Any]] = None
    receipt_file_id: Optional[str] = None


class AgentTraceItem(BaseModel):
    agent: str
    action: str
    result_summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskResponse(BaseModel):
    task_id: str
    requester_id: str
    input_text: str
    status: TaskStatus
    plan: Optional[Dict[str, Any]] = None
    receipt_data: Optional[Dict[str, Any]] = None
    validation_findings: Optional[Dict[str, Any]] = None
    proposed_action: Optional[Dict[str, Any]] = None
    governance_decision: Optional[str] = None
    governance_reasons: List[str] = Field(default_factory=list)
    risk_assessment: Optional[Dict[str, Any]] = None
    approval_id: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    claim_id: Optional[str] = None
    error: Optional[str] = None
    agent_trace: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class AgentTaskInDB(TaskResponse):
    input_data: Optional[Dict[str, Any]] = None
    checkpoint_ref: Optional[str] = None
