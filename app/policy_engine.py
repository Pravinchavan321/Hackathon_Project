"""Deterministic policy gate. No LLM here. Fails closed on any error."""
import hashlib
import json
import math
import os
import yaml

POLICY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "policies.yaml")


def load_policy(path=POLICY_PATH):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def canonical_action(action):
    """Stable string of everything that matters for execution (the free-text note is excluded)."""
    args = action.get("args") or {}
    core = {"tool": action.get("tool"), "args": {k: args[k] for k in sorted(args) if k != "note"}}
    return json.dumps(core, sort_keys=True, separators=(",", ":"))


def action_hash(action):
    return hashlib.sha256(canonical_action(action).encode()).hexdigest()[:16]


def _amount(args):
    a = args.get("amount")
    if isinstance(a, bool) or not isinstance(a, (int, float)) or not math.isfinite(a) or a <= 0:
        raise ValueError("invalid amount")
    return float(a)


def _evaluate(action, env, policy):
    tool = action.get("tool")
    if tool not in policy["tool_allowlist"]:
        return {"decision": "BLOCK", "reasons": ["R0_TOOL_NOT_ALLOWED"], "action_hash": action_hash(action)}
    if tool != "submit_claim":
        return {"decision": "ALLOW", "reasons": [], "action_hash": action_hash(action)}
    args = action.get("args") or {}
    try:
        amount = _amount(args)
    except ValueError:
        return {"decision": "BLOCK", "reasons": ["R0_INVALID_INPUT"], "action_hash": action_hash(action)}
    rid = str(args.get("receipt_id") or "").strip()
    emp = args.get("employee")
    block, esc = [], []
    for rule in policy["rules"]:
        t = rule["type"]
        if t == "receipt_required":
            hit = not rid
        elif t == "banned_category":
            hit = str(args.get("category", "")).lower() in rule["categories"]
        elif t == "duplicate_receipt":
            hit = bool(rid) and rid in env.seen_receipts
        elif t == "amount_over":
            hit = amount > rule["limit"]
        elif t == "daily_cap":
            hit = env.daily_spent.get(emp, 0) + amount > rule["limit"]
        else:
            raise ValueError("unknown rule type " + str(t))
        if hit:
            (block if rule["decision"] == "BLOCK" else esc).append(rule["id"])
    if block:
        return {"decision": "BLOCK", "reasons": block + esc, "action_hash": action_hash(action)}
    if esc:
        return {"decision": "ESCALATE", "reasons": esc, "action_hash": action_hash(action)}
    return {"decision": "ALLOW", "reasons": [], "action_hash": action_hash(action)}


def evaluate(action, env, policy=None):
    """Returns {decision, reasons, action_hash}. Any exception => BLOCK (fail closed).
    Agent-supplied flags such as action['approved'] are never read."""
    try:
        return _evaluate(action, env, policy or load_policy())
    except Exception as e:
        return {"decision": "BLOCK", "reasons": ["FAIL_CLOSED"], "action_hash": None, "error": type(e).__name__}


def verify_approval(approval, action, policy=None):
    """Approval must be: approved, from an allowed role, and bound to the exact current action."""
    policy = policy or load_policy()
    if not isinstance(approval, dict) or approval.get("verdict") != "approved":
        return False, "NOT_APPROVED"
    if approval.get("approver_role") not in policy["approval"]["who_can_approve"]:
        return False, "APPROVER_NOT_AUTHORIZED"
    if approval.get("action_hash") != action_hash(action):
        return False, "ACTION_CHANGED"
    return True, "OK"
