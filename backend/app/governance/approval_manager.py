"""Human Approval Manager with Exact-Action Cryptographic Binding."""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from backend.app.governance.policy_engine import compute_action_hash
from backend.app.database import collections

# In-memory approval storage for offline/testing mode
_MEMORY_APPROVALS: Dict[str, Dict[str, Any]] = {}
_CONSUMED_APPROVALS = set()


class ApprovalManager:
    """Manages the lifecycle of human approval tickets."""

    def __init__(self, db=None):
        self.db = db

    def create_approval_request(
        self,
        task_id: str,
        requester_id: str,
        action: Dict[str, Any],
        reasons: list,
        risk_assessment: Optional[Dict[str, Any]] = None,
        claim_id: Optional[str] = None,
        ttl_minutes: int = 60,
    ) -> str:
        """Create a pending approval ticket cryptographically bound to action hash."""
        approval_id = "appr-" + uuid.uuid4().hex[:8]
        act_hash = compute_action_hash(action)
        now = datetime.utcnow()
        expires = now + timedelta(minutes=ttl_minutes)

        doc = {
            "approval_id": approval_id,
            "task_id": task_id,
            "claim_id": claim_id,
            "requester_id": requester_id,
            "approver_id": None,
            "approver_role": None,
            "action_hash": act_hash,
            "proposed_action": action,
            "reasons": reasons,
            "risk_assessment": risk_assessment or {},
            "status": "PENDING",
            "reason": None,
            "expires_at": expires,
            "consumed_at": None,
            "created_at": now,
            "updated_at": now,
        }

        if self.db is not None:
            self.db[collections.APPROVALS].insert_one(doc)
        _MEMORY_APPROVALS[approval_id] = doc

        return approval_id

    def get_approval(self, approval_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve approval record by ID."""
        if self.db is not None:
            return self.db[collections.APPROVALS].find_one({"approval_id": approval_id})
        return _MEMORY_APPROVALS.get(approval_id)

    def record_decision(
        self, approval_id: str, approver_id: str, approver_role: str, verdict: str, reason: str = ""
    ) -> Tuple[bool, str]:
        """Record manager approve or reject decision."""
        if verdict not in ["approved", "rejected"]:
            return False, "INVALID_VERDICT"

        now = datetime.utcnow()
        new_status = "APPROVED" if verdict == "approved" else "REJECTED"

        # Check in DB or Memory
        appr = self.get_approval(approval_id)
        if not appr:
            return False, "APPROVAL_NOT_FOUND"

        if appr.get("status") != "PENDING":
            return False, f"CANNOT_DECIDE_STATUS_{appr.get('status')}"

        if now > appr.get("expires_at", now):
            return False, "APPROVAL_EXPIRED"

        update_fields = {
            "status": new_status,
            "approver_id": approver_id,
            "approver_role": approver_role,
            "reason": reason,
            "updated_at": now,
        }

        if self.db is not None:
            self.db[collections.APPROVALS].update_one(
                {"approval_id": approval_id, "status": "PENDING"},
                {"$set": update_fields},
            )
        if approval_id in _MEMORY_APPROVALS:
            _MEMORY_APPROVALS[approval_id].update(update_fields)

        return True, new_status

    def verify_and_consume(
        self, approval_id: str, current_action: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Atomic verification and consumption of approval ticket.
        Verifies: status==APPROVED, action_hash matches current_action, not expired, single-use.
        """
        appr = self.get_approval(approval_id)
        if not appr:
            return False, "APPROVAL_NOT_FOUND"

        if appr.get("status") != "APPROVED":
            return False, f"APPROVAL_STATUS_IS_{appr.get('status')}"

        # 1. Exact-Action Hash Verification (Tamper Check)
        current_hash = compute_action_hash(current_action)
        if appr.get("action_hash") != current_hash:
            return False, "ACTION_CHANGED_TAMPER_DETECTED"

        # 2. Expiry Check
        if datetime.utcnow() > appr.get("expires_at"):
            return False, "APPROVAL_EXPIRED"

        # 3. Single-Use Check (Replay Prevention)
        consumption_key = (approval_id, appr.get("action_hash"))
        if consumption_key in _CONSUMED_APPROVALS or appr.get("consumed_at") is not None:
            return False, "APPROVAL_ALREADY_CONSUMED"

        # Atomic consume
        now = datetime.utcnow()
        if self.db is not None:
            res = self.db[collections.APPROVALS].find_one_and_update(
                {"approval_id": approval_id, "status": "APPROVED", "consumed_at": None},
                {"$set": {"consumed_at": now, "status": "CONSUMED"}},
            )
            if not res:
                return False, "APPROVAL_CONCURRENTLY_CONSUMED"

        _CONSUMED_APPROVALS.add(consumption_key)
        if approval_id in _MEMORY_APPROVALS:
            _MEMORY_APPROVALS[approval_id]["consumed_at"] = now
            _MEMORY_APPROVALS[approval_id]["status"] = "CONSUMED"

        return True, "OK"
