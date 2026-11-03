"""Append-Only Audit Service for AgentShield AI."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.app.database import collections

_MEMORY_AUDIT_LOGS: List[Dict[str, Any]] = []


class AuditService:
    """Records security-critical governance events and decisions."""

    def __init__(self, db=None):
        self.db = db

    def log_event(
        self,
        actor_id: str,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        decision: Optional[str] = None,
        reason_codes: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        task_id: Optional[str] = None,
        claim_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> str:
        """Create an append-only audit event document."""
        event_id = "evt-" + uuid.uuid4().hex[:10]
        now = datetime.utcnow()

        doc = {
            "event_id": event_id,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "decision": decision,
            "reason_codes": reason_codes or [],
            "details": details or {},
            "correlation_id": correlation_id or ("corr-" + uuid.uuid4().hex[:8]),
            "task_id": task_id,
            "claim_id": claim_id,
            "ip_address": ip_address,
            "timestamp": now,
        }

        if self.db is not None:
            try:
                self.db[collections.AUDIT_LOGS].insert_one(doc)
            except Exception:
                pass

        _MEMORY_AUDIT_LOGS.append(doc)
        return event_id

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch latest audit records."""
        if self.db is not None:
            try:
                cursor = self.db[collections.AUDIT_LOGS].find().sort("timestamp", -1).limit(limit)
                return list(cursor)
            except Exception:
                pass
        return _MEMORY_AUDIT_LOGS[-limit:]
