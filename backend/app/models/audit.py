"""Audit Log models and schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AuditEventResponse(BaseModel):
    event_id: str
    actor_id: str
    actor_role: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    decision: Optional[str] = None
    reason_codes: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str
    task_id: Optional[str] = None
    claim_id: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
