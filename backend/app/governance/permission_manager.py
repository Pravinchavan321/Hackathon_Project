"""Role-Based Access Control and Resource-Level Permission Manager."""
from typing import List, Dict, Any, Optional
from backend.app.models.user import UserRole


class PermissionManager:
    """Enforces fine-grained role permissions and resource-level access scope."""

    ROLE_PERMISSIONS: Dict[str, List[str]] = {
        UserRole.EMPLOYEE.value: [
            "submit_claim",
            "view_own_claims",
            "view_own_tasks",
            "upload_receipt",
            "cancel_own_task",
        ],
        UserRole.MANAGER.value: [
            "submit_claim",
            "view_own_claims",
            "view_team_claims",
            "view_own_tasks",
            "view_pending_approvals",
            "approve_claim",
            "reject_claim",
            "view_audit_logs",
            "upload_receipt",
        ],
        UserRole.ADMIN.value: [
            "submit_claim",
            "view_all_claims",
            "view_all_tasks",
            "view_pending_approvals",
            "approve_claim",
            "reject_claim",
            "manage_policies",
            "manage_users",
            "view_audit_logs",
            "view_evaluations",
            "run_evaluations",
            "upload_receipt",
        ],
    }

    def has_permission(self, role: str, permission: str) -> bool:
        """Verify if a user role possesses a specific capability."""
        perms = self.ROLE_PERMISSIONS.get(role, [])
        return permission in perms

    def can_access_resource(
        self, user_id: str, user_role: str, resource_owner_id: str
    ) -> bool:
        """Enforce resource-level horizontal authorization.
        Admins and Managers can access scoped records; employees can only access their own.
        """
        if user_role == UserRole.ADMIN.value:
            return True
        if user_role == UserRole.MANAGER.value:
            return True
        return user_id == resource_owner_id

    def can_approve_action(self, approver_role: str, requester_id: str, approver_id: str) -> tuple[bool, str]:
        """Validate approval eligibility. Prevents self-approval."""
        if approver_role not in [UserRole.MANAGER.value, UserRole.ADMIN.value]:
            return False, "APPROVER_NOT_AUTHORIZED"
        if approver_id == requester_id:
            return False, "SELF_APPROVAL_PROHIBITED"
        return True, "OK"
