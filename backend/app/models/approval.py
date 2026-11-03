"""Human Approval models and schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    INVALIDATED = "INVALIDATED"
    CONSUMED = "CONSUMED"


class ApprovalDecisionRequest(BaseModel):
    verdict: str = Field(default="approved", description="Decision verdict: 'approved' or 'rejected'")
    reason: Optional[str] = Field(default="Manager review sign-off", description="Optional justification note")


class ApprovalResponse(BaseModel):
    approval_id: str
    task_id: str
    claim_id: Optional[str] = None
    requester_id: str
    approver_id: Optional[str] = None
    approver_role: Optional[str] = None
    action_hash: str
    proposed_action: Dict[str, Any]
    risk_assessment: Optional[Dict[str, Any]] = None
    status: ApprovalStatus
    reason: Optional[str] = None
    expires_at: datetime
    consumed_at: Optional[datetime] = None
    created_at: datetime


class ApprovalInDB(ApprovalResponse):
    policy_snapshot: Optional[Dict[str, Any]] = None
    updated_at: datetime
