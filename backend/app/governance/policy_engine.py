"""Deterministic Policy Engine for AgentShield AI.
Evaluates proposed actions against organizational policies. No LLM in the loop.
Strict fail-closed architecture with BLOCK > ESCALATE > ALLOW precedence.
"""
import hashlib
import json
import math
import os
import yaml
from typing import Dict, Any, List, Optional
from backend.app.database import collections

SEED_POLICY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "policies_seed.yaml"
)
ROOT_POLICY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "policies.yaml"
)


def canonical_action(action: Dict[str, Any]) -> str:
    """Deterministic canonical serialization of execution parameters.
    Excludes non-execution free-text notes so comments don't break approvals.
    """
    args = action.get("args") or action.get("parameters") or {}
    core = {
        "tool": action.get("tool") or action.get("operation"),
        "args": {k: args[k] for k in sorted(args.keys()) if k not in ["note", "comment"]},
    }
    return json.dumps(core, sort_keys=True, separators=(",", ":"))


def compute_action_hash(action: Dict[str, Any]) -> str:
    """Generate SHA-256 digest of canonical execution parameters (first 16 hex chars)."""
    return hashlib.sha256(canonical_action(action).encode("utf-8")).hexdigest()[:16]


class PolicyEngine:
    """Evaluates proposed actions deterministically against active policies."""

    def __init__(self, db=None, policy_path: Optional[str] = None):
        self.db = db
        self.policy_path = policy_path or (ROOT_POLICY_PATH if os.path.exists(ROOT_POLICY_PATH) else SEED_POLICY_PATH)
        self._cached_policy: Optional[Dict[str, Any]] = None

    def load_active_policy(self) -> Dict[str, Any]:
        """Load active policy from MongoDB or fallback to YAML seed file."""
        if self.db is not None:
            try:
                active_doc = self.db[collections.POLICIES].find_one({"active": True}, sort=[("version", -1)])
                if active_doc:
                    return active_doc
            except Exception:
                pass

        if os.path.exists(self.policy_path):
            with open(self.policy_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

        # Default minimal hardcoded safety fallback
        return {
            "version": 1,
            "tool_allowlist": ["submit_claim", "get_policy", "notify_manager"],
            "rules": [
                {"id": "R1_AMOUNT_LIMIT", "type": "amount_over", "limit": 5000, "decision": "ESCALATE"},
                {"id": "R2_BANNED_CATEGORY", "type": "banned_category", "categories": ["personal", "alcohol", "gambling", "gift_cards"], "decision": "BLOCK"},
                {"id": "R3_DUPLICATE_RECEIPT", "type": "duplicate_receipt", "decision": "BLOCK"},
                {"id": "R4_DAILY_CAP", "type": "daily_cap", "limit": 10000, "decision": "ESCALATE"},
                {"id": "R5_RECEIPT_REQUIRED", "type": "receipt_required", "decision": "BLOCK"},
            ],
            "approval": {"who_can_approve": ["MANAGER", "ADMIN"], "single_use": True},
        }

    def evaluate(self, action: Dict[str, Any], env: Any = None) -> Dict[str, Any]:
        """Evaluate proposed action against active policy rules.
        Returns: {decision: "ALLOW"|"ESCALATE"|"BLOCK", reasons: [...], action_hash: "..."}
        Fails closed on any exception.
        """
        try:
            policy = self.load_active_policy()
            act_hash = compute_action_hash(action)
            tool = action.get("tool") or action.get("operation")
            allowlist = policy.get("tool_allowlist", [])

            # 1. Tool Allowlist Check
            if tool not in allowlist:
                return {
                    "decision": "BLOCK",
                    "reasons": ["R0_TOOL_NOT_ALLOWED"],
                    "action_hash": act_hash,
                }

            # Non-claim tools on allowlist pass
            if tool != "submit_claim":
                return {
                    "decision": "ALLOW",
                    "reasons": [],
                    "action_hash": act_hash,
                }

            args = action.get("args") or action.get("parameters") or {}

            # Amount validation
            raw_amt = args.get("amount")
            if isinstance(raw_amt, bool) or not isinstance(raw_amt, (int, float)) or not math.isfinite(raw_amt) or raw_amt <= 0:
                return {
                    "decision": "BLOCK",
                    "reasons": ["R0_INVALID_INPUT"],
                    "action_hash": act_hash,
                }
            amount = float(raw_amt)

            rid = str(args.get("receipt_id") or "").strip()
            emp = args.get("employee") or args.get("user_id") or ""
            category = str(args.get("category", "")).lower().strip()

            blocks: List[str] = []
            escalates: List[str] = []

            rules = policy.get("rules", [])
            for rule in rules:
                rtype = rule.get("type") or rule.get("rule_type")
                rdec = rule.get("decision", "BLOCK")
                rid_name = rule.get("id") or rule.get("rule_id", "RULE")
                params = rule.get("parameters", {})

                hit = False
                if rtype in ["receipt_required"]:
                    hit = not rid
                elif rtype in ["banned_category", "category_blocked"]:
                    cats = rule.get("categories") or params.get("categories", [])
                    hit = category in [c.lower() for c in cats]
                elif rtype in ["duplicate_receipt", "duplicate_check"]:
                    seen = getattr(env, "seen_receipts", set()) if env else set()
                    hit = bool(rid) and (rid in seen)
                elif rtype in ["amount_over", "amount_threshold"]:
                    limit = rule.get("limit") or params.get("threshold", 5000)
                    hit = amount > limit
                elif rtype in ["daily_cap", "daily_limit"]:
                    daily_spent = getattr(env, "daily_spent", {}) if env else {}
                    limit = rule.get("limit") or params.get("limit", 10000)
                    hit = (daily_spent.get(emp, 0) + amount) > limit

                if hit:
                    if rdec in ["BLOCK", "DENY"]:
                        blocks.append(rid_name)
                    else:
                        escalates.append(rid_name)

            # Precedence: BLOCK > ESCALATE > ALLOW
            if blocks:
                return {
                    "decision": "BLOCK",
                    "reasons": blocks + escalates,
                    "action_hash": act_hash,
                }
            if escalates:
                return {
                    "decision": "ESCALATE",
                    "reasons": escalates,
                    "action_hash": act_hash,
                }
            return {
                "decision": "ALLOW",
                "reasons": [],
                "action_hash": act_hash,
            }

        except Exception as e:
            # FAIL CLOSED: Any unexpected error results in BLOCK
            return {
                "decision": "BLOCK",
                "reasons": ["FAIL_CLOSED"],
                "action_hash": None,
                "error": type(e).__name__,
            }
