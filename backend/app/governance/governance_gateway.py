"""Governance Gateway — The Single Mandatory Authorization Boundary for AgentShield AI.
No agent can execute a sensitive tool directly; all proposed actions must pass through here.
"""
from typing import Dict, Any, Optional
from backend.app.governance.policy_engine import PolicyEngine, compute_action_hash
from backend.app.governance.permission_manager import PermissionManager
from backend.app.governance.risk_engine import RiskEngine
from backend.app.governance.approval_manager import ApprovalManager
from backend.app.governance.audit_service import AuditService


class GovernanceGateway:
    """The central deterministic control plane for AI agent execution."""

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        permission_manager: Optional[PermissionManager] = None,
        risk_engine: Optional[RiskEngine] = None,
        approval_manager: Optional[ApprovalManager] = None,
        audit_service: Optional[AuditService] = None,
        db=None,
    ):
        self.db = db
        self.policy_engine = policy_engine or PolicyEngine(db=db)
        self.permission_manager = permission_manager or PermissionManager()
        self.risk_engine = risk_engine or RiskEngine()
        self.approval_manager = approval_manager or ApprovalManager(db=db)
        self.audit_service = audit_service or AuditService(db=db)

    def evaluate(
        self,
        proposed_action: Dict[str, Any],
        context: Dict[str, Any],
        env: Any = None,
        approval_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Comprehensive Governance Evaluation:
        1. Validate principal permissions
        2. Evaluate deterministic policies (BLOCK > ESCALATE > ALLOW)
        3. Compute explainable risk assessment
        4. If approval present, revalidate exact action hash and single-use status
        5. Log audit event
        6. Return ALLOW, DENY, or REQUIRE_APPROVAL
        """
        user_id = context.get("user_id", "anonymous")
        user_role = context.get("user_role", "EMPLOYEE")
        task_id = context.get("task_id", "task-default")
        act_hash = compute_action_hash(proposed_action)

        # 1. Base RBAC Check
        tool_name = proposed_action.get("tool") or proposed_action.get("operation", "")
        if tool_name == "submit_claim" and not self.permission_manager.has_permission(user_role, "submit_claim"):
            self.audit_service.log_event(
                actor_id=user_id,
                actor_role=user_role,
                action="governance_evaluate",
                resource_type="claim",
                decision="DENY",
                reason_codes=["PERMISSION_DENIED"],
                task_id=task_id,
            )
            return {
                "decision": "DENY",
                "reasons": ["PERMISSION_DENIED"],
                "action_hash": act_hash,
                "approval_id": None,
            }

        # 2. Policy Engine Evaluation
        policy_res = self.policy_engine.evaluate(proposed_action, env=env)
        policy_dec = policy_res.get("decision", "BLOCK")
        reasons = policy_res.get("reasons", [])

        # 3. Risk Assessment
        risk = self.risk_engine.assess(proposed_action, context, policy_res)

        # Precedence Step: If Policy says BLOCK -> unconditionally DENY
        if policy_dec == "BLOCK":
            self.audit_service.log_event(
                actor_id=user_id,
                actor_role=user_role,
                action="governance_evaluate",
                resource_type="claim",
                decision="DENY",
                reason_codes=reasons,
                details={"risk": risk, "action_hash": act_hash},
                task_id=task_id,
            )
            return {
                "decision": "DENY",
                "reasons": reasons,
                "risk": risk,
                "action_hash": act_hash,
                "approval_id": None,
            }

        # Precedence Step: If Policy says ESCALATE -> Check or Create Human Approval
        if policy_dec == "ESCALATE":
            if not approval_id:
                # Create pending approval request
                appr_id = self.approval_manager.create_approval_request(
                    task_id=task_id,
                    requester_id=user_id,
                    action=proposed_action,
                    reasons=reasons,
                    risk_assessment=risk,
                )
                self.audit_service.log_event(
                    actor_id=user_id,
                    actor_role=user_role,
                    action="approval_requested",
                    resource_type="approval",
                    resource_id=appr_id,
                    decision="REQUIRE_APPROVAL",
                    reason_codes=reasons,
                    task_id=task_id,
                )
                return {
                    "decision": "REQUIRE_APPROVAL",
                    "reasons": reasons,
                    "risk": risk,
                    "action_hash": act_hash,
                    "approval_id": appr_id,
                }
            else:
                # Revalidate existing approval ticket
                valid, why = self.approval_manager.verify_and_consume(approval_id, proposed_action)
                if not valid:
                    self.audit_service.log_event(
                        actor_id=user_id,
                        actor_role=user_role,
                        action="approval_revalidation_failed",
                        resource_type="approval",
                        resource_id=approval_id,
                        decision="DENY",
                        reason_codes=[why],
                        task_id=task_id,
                    )
                    return {
                        "decision": "DENY",
                        "reasons": [why],
                        "risk": risk,
                        "action_hash": act_hash,
                        "approval_id": approval_id,
                    }
                # Approval verified and consumed successfully! Fresh state passes
                self.audit_service.log_event(
                    actor_id=user_id,
                    actor_role=user_role,
                    action="approval_verified_execution_allowed",
                    resource_type="approval",
                    resource_id=approval_id,
                    decision="ALLOW",
                    reason_codes=["APPROVED_BY_MANAGER"],
                    task_id=task_id,
                )
                return {
                    "decision": "ALLOW",
                    "reasons": ["APPROVED_BY_MANAGER"],
                    "risk": risk,
                    "action_hash": act_hash,
                    "approval_id": approval_id,
                }

        # Policy says ALLOW
        self.audit_service.log_event(
            actor_id=user_id,
            actor_role=user_role,
            action="governance_evaluate",
            resource_type="claim",
            decision="ALLOW",
            reason_codes=[],
            details={"risk": risk, "action_hash": act_hash},
            task_id=task_id,
        )
        return {
            "decision": "ALLOW",
            "reasons": [],
            "risk": risk,
            "action_hash": act_hash,
            "approval_id": None,
        }
