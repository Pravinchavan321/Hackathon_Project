"""Policy rule models and schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class PolicyDecisionType(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class PolicyRule(BaseModel):
    rule_id: str
    rule_type: str  # amount_threshold, category_blocked, duplicate_check, daily_limit, receipt_required
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    decision: PolicyDecisionType
    priority: int = 10


class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    rules: List[PolicyRule]
    active: bool = True


class PolicyUpdate(BaseModel):
    description: Optional[str] = None
    rules: Optional[List[PolicyRule]] = None
    active: Optional[bool] = None


class PolicyResponse(PolicyCreate):
    policy_id: str
    version: int
    created_by: str
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
