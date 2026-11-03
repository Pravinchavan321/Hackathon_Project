"""Phase 4 Verification Tests — Independent Governance Engine."""
import pytest
from backend.app.governance.policy_engine import PolicyEngine, compute_action_hash
from backend.app.governance.permission_manager import PermissionManager
from backend.app.governance.risk_engine import RiskEngine
from backend.app.governance.approval_manager import ApprovalManager
from backend.app.governance.governance_gateway import GovernanceGateway
from backend.app.models.user import UserRole


class MockWorldEnv:
    def __init__(self, seen_receipts=None, daily_spent=None):
        self.seen_receipts = set(seen_receipts or [])
        self.daily_spent = dict(daily_spent or {})


def create_action(amount=1000.0, category="travel", receipt_id="R-001", tool="submit_claim", note=""):
    return {
        "tool": tool,
        "args": {
            "amount": amount,
            "category": category,
            "receipt_id": receipt_id,
            "employee": "E-001",
            "note": note,
        },
        "approved": False,
    }


@pytest.fixture
def gateway():
    return GovernanceGateway()


def test_boundary_4999_allow(gateway):
    """Amount of ₹4,999 is below threshold and should be allowed automatically."""
    action = create_action(amount=4999.0)
    context = {"user_id": "u-001", "user_role": "EMPLOYEE"}
    res = gateway.evaluate(action, context, env=MockWorldEnv())
    assert res["decision"] == "ALLOW"
    assert res["reasons"] == []


def test_boundary_5000_allow(gateway):
    """Amount of exactly ₹5,000 is allowed (condition is strictly > 5000)."""
    action = create_action(amount=5000.0)
    context = {"user_id": "u-001", "user_role": "EMPLOYEE"}
    res = gateway.evaluate(action, context, env=MockWorldEnv())
    assert res["decision"] == "ALLOW"


def test_boundary_5001_require_approval(gateway):
    """Amount of ₹5,001 exceeds threshold and must require human approval."""
    action = create_action(amount=5001.0)
    context = {"user_id": "u-001", "user_role": "EMPLOYEE"}
    res = gateway.evaluate(action, context, env=MockWorldEnv())
    assert res["decision"] == "REQUIRE_APPROVAL"
    assert "R1_AMOUNT_LIMIT" in res["reasons"]
    assert res["approval_id"] is not None


def test_banned_category_blocks(gateway):
    """Banned categories (gambling, alcohol, etc.) must be unconditionally blocked."""
    action = create_action(amount=800.0, category="gambling")
    context = {"user_id": "u-001", "user_role": "EMPLOYEE"}
    res = gateway.evaluate(action, context, env=MockWorldEnv())
    assert res["decision"] == "DENY"
    assert "R2_BANNED_CATEGORY" in res["reasons"]


def test_duplicate_receipt_blocks(gateway):
    """Recycling an already-claimed receipt must be blocked."""
    env = MockWorldEnv(seen_receipts=["R-USED-99"])
    action = create_action(amount=1200.0, receipt_id="R-USED-99")
    context = {"user_id": "u-001", "user_role": "EMPLOYEE"}
    res = gateway.evaluate(action, context, env=env)
    assert res["decision"] == "DENY"
    assert "R3_DUPLICATE_RECEIPT" in res["reasons"]


def test_missing_receipt_blocks(gateway):
    """A claim without a receipt attached must be blocked."""
    action = create_action(amount=800.0, receipt_id="")
    context = {"user_id": "u-001", "user_role": "EMPLOYEE"}
    res = gateway.evaluate(action, context, env=MockWorldEnv())
    assert res["decision"] == "DENY"
    assert "R5_RECEIPT_REQUIRED" in res["reasons"]


def test_tool_not_on_allowlist_blocks(gateway):
    """Adversarial invocation of unapproved tool (e.g. transfer_funds) must be blocked."""
    action = create_action(amount=2000.0, tool="transfer_funds")
    context = {"user_id": "u-001", "user_role": "EMPLOYEE"}
    res = gateway.evaluate(action, context, env=MockWorldEnv())
    assert res["decision"] == "DENY"
    assert "R0_TOOL_NOT_ALLOWED" in res["reasons"]


def test_agent_approved_flag_is_ignored(gateway):
    """Agent injecting approved=True inside proposal must be ignored by governance."""
    action = create_action(amount=9000.0)
    action["approved"] = True  # LLM prompt injection simulation
    context = {"user_id": "u-001", "user_role": "EMPLOYEE"}
    res = gateway.evaluate(action, context, env=MockWorldEnv())
    assert res["decision"] == "REQUIRE_APPROVAL"  # Gateway still forces approval


def test_exact_action_hash_tamper_detection():
    """Modifying execution parameters must change the action digest and fail revalidation."""
    a1 = create_action(amount=9000.0, receipt_id="R-ORIGINAL")
    a2 = create_action(amount=9000.0, receipt_id="R-TAMPERED")
    a3 = create_action(amount=9001.0, receipt_id="R-ORIGINAL")
    a4 = create_action(amount=9000.0, receipt_id="R-ORIGINAL", note="Different comment")

    h1 = compute_action_hash(a1)
    h2 = compute_action_hash(a2)
    h3 = compute_action_hash(a3)
    h4 = compute_action_hash(a4)

    assert h1 != h2, "Receipt modification must change hash"
    assert h1 != h3, "Amount modification must change hash"
    assert h1 == h4, "Free-form comments must NOT affect action digest"


def test_approval_lifecycle_and_single_use(gateway):
    """Test full approval lifecycle: pause, approve, revalidate, consume, and prevent replay."""
    action = create_action(amount=8500.0)
    context = {"user_id": "u-emp01", "user_role": "EMPLOYEE", "task_id": "t-100"}

    # 1. Initial evaluation -> REQUIRE_APPROVAL
    init_res = gateway.evaluate(action, context, env=MockWorldEnv())
    assert init_res["decision"] == "REQUIRE_APPROVAL"
    appr_id = init_res["approval_id"]

    # 2. Manager approves
    ok, status = gateway.approval_manager.record_decision(
        approval_id=appr_id,
        approver_id="u-mgr01",
        approver_role="MANAGER",
        verdict="approved",
        reason="Verified business expense",
    )
    assert ok is True
    assert status == "APPROVED"

    # 3. Workflow resumes with approval_id -> ALLOW
    resume_res = gateway.evaluate(action, context, env=MockWorldEnv(), approval_id=appr_id)
    assert resume_res["decision"] == "ALLOW"

    # 4. Attempting to REUSE same approval ticket -> must fail (single-use enforced)
    replay_res = gateway.evaluate(action, context, env=MockWorldEnv(), approval_id=appr_id)
    assert replay_res["decision"] == "DENY"
    assert "APPROVAL_ALREADY_CONSUMED" in replay_res["reasons"] or "APPROVAL_STATUS_IS_CONSUMED" in replay_res["reasons"]


def test_self_approval_prevention():
    """An employee or manager cannot approve their own expense claim."""
    perm_mgr = PermissionManager()
    ok, why = perm_mgr.can_approve_action(
        approver_role="MANAGER",
        requester_id="u-same-user",
        approver_id="u-same-user",
    )
    assert ok is False
    assert why == "SELF_APPROVAL_PROHIBITED"
