"""Controlled Claim Execution Tool for AgentShield AI.
SIMULATED business process (no real money transfer).
STRICT SECURITY BOUNDARY: Can ONLY be invoked when presented with a valid Governance Gateway ALLOW ticket.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from backend.app.database import collections
from backend.app.tools.duplicate_checker import compute_claim_fingerprint, DuplicateChecker

_MEMORY_EXECUTIONS: Dict[str, Dict[str, Any]] = {}
_MEMORY_CLAIMS: Dict[str, Dict[str, Any]] = {}
_USED_IDEMPOTENCY_KEYS = set()


class ClaimExecutor:
    """Executes simulated expense reimbursement after governance authorization."""

    def __init__(self, db=None, duplicate_checker: Optional[DuplicateChecker] = None):
        self.db = db
        self.duplicate_checker = duplicate_checker or DuplicateChecker(db=db)

    def execute_claim_submission(
        self,
        proposed_action: Dict[str, Any],
        user_id: str,
        task_id: str,
        governance_ticket: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        approved_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute claim creation under strict governance conditions."""
        # 1. HARD SECURITY CHECK: Valid Governance ALLOW ticket required
        if not governance_ticket or governance_ticket.get("decision") != "ALLOW":
            raise PermissionError(
                f"Unauthorized tool invocation blocked: Governance decision is {governance_ticket.get('decision') if governance_ticket else 'MISSING'}"
            )

        # 2. Idempotency Check (Prevents duplicate execution on network retry)
        idem_key = idempotency_key or f"idem-{task_id}"
        if idem_key in _USED_IDEMPOTENCY_KEYS:
            return {
                "ok": True,
                "status": "SUBMITTED_ALREADY_IDEMPOTENT",
                "idempotency_key": idem_key,
                "message": "Transaction already executed; returning cached success.",
            }

        args = proposed_action.get("args") or proposed_action.get("parameters") or {}
        amount = float(args.get("amount", 0.0))
        category = str(args.get("category", "travel"))
        receipt_id = args.get("receipt_id")
        merchant = args.get("merchant", "Simulated Merchant")
        expense_date = args.get("expense_date")

        claim_id = "clm-" + uuid.uuid4().hex[:8]
        exec_id = "exec-" + uuid.uuid4().hex[:8]
        now = datetime.utcnow()

        # Create tool execution record
        exec_doc = {
            "execution_id": exec_id,
            "task_id": task_id,
            "tool_name": "submit_claim",
            "action_hash": governance_ticket.get("action_hash"),
            "parameters": args,
            "status": "SUCCEEDED",
            "idempotency_key": idem_key,
            "approved_by": approved_by,
            "created_at": now,
        }

        # Create simulated expense claim document
        claim_doc = {
            "claim_id": claim_id,
            "user_id": user_id,
            "amount": amount,
            "currency": "INR",
            "category": category,
            "merchant": merchant,
            "expense_date": expense_date,
            "status": "SUBMITTED",
            "receipt_id": receipt_id,
            "task_id": task_id,
            "action_hash": governance_ticket.get("action_hash"),
            "idempotency_key": idem_key,
            "created_at": now,
            "updated_at": now,
            "simulated": True,
        }

        if self.db is not None:
            self.db[collections.TOOL_EXECUTIONS].insert_one(exec_doc)
            self.db[collections.EXPENSE_CLAIMS].insert_one(claim_doc)

        _MEMORY_EXECUTIONS[exec_id] = exec_doc
        _MEMORY_CLAIMS[claim_id] = claim_doc
        _USED_IDEMPOTENCY_KEYS.add(idem_key)

        # Record fingerprint in duplicate checker
        fp = compute_claim_fingerprint(user_id, amount, category, expense_date)
        self.duplicate_checker.record_seen(claim_fingerprint=fp)

        return {
            "ok": True,
            "claim_id": claim_id,
            "execution_id": exec_id,
            "status": "SUBMITTED",
            "amount": amount,
            "currency": "INR",
            "simulated": True,
            "created_at": now.isoformat(),
        }
