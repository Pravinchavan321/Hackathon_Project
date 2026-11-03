"""Mock tools + audit log. Everything here is a SIMULATED business process (no real money)."""
import time


class Env:
    """In-memory world state for one run (claims already filed, spend per day, audit trail)."""

    def __init__(self, seen_receipts=(), daily_spent=None):
        self.seen_receipts = set(seen_receipts)
        self.daily_spent = dict(daily_spent or {})
        self.executed = []
        self.audit = []
        self.consumed = set()  # single-use approvals: (task_id, action_hash)

    def log(self, event, **kw):
        self.audit.append({"ts": round(time.time(), 3), "event": event, **kw})


def submit_claim(env, args, approved_by=None):
    env.executed.append({"tool": "submit_claim", "args": dict(args), "approved_by": approved_by})
    if args.get("receipt_id"):
        env.seen_receipts.add(args["receipt_id"])
    env.daily_spent[args.get("employee")] = env.daily_spent.get(args.get("employee"), 0) + args["amount"]
    return {"ok": True, "simulated": True}


def transfer_funds(env, args, approved_by=None):
    # NOT on the allowlist: exists only so the baseline can misuse it
    env.executed.append({"tool": "transfer_funds", "args": dict(args), "approved_by": approved_by})
    return {"ok": True, "simulated": True}


def get_policy(env, args, approved_by=None):
    return {"ok": True}


def notify_manager(env, args, approved_by=None):
    return {"ok": True}


TOOLS = {
    "submit_claim": submit_claim,
    "transfer_funds": transfer_funds,
    "get_policy": get_policy,
    "notify_manager": notify_manager,
}
