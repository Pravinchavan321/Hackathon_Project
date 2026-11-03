"""Approval API Routes for AgentShield AI.
Endpoints for managers to inspect pending human-in-the-loop approvals, review exact proposals,
and sign-off / reject with cryptographic action hash validation.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.middleware.auth_middleware import get_current_user, require_role
from backend.app.models.user import UserRole
from backend.app.models.approval import ApprovalDecisionRequest
from backend.app.governance.approval_manager import ApprovalManager

router = APIRouter()
approval_manager = ApprovalManager()


@router.get("/pending", tags=["Approvals"])
async def get_pending_approvals(
    current_user: dict = Depends(require_role([UserRole.MANAGER, UserRole.ADMIN])),
) -> List[Dict[str, Any]]:
    """Retrieve all pending approval requests awaiting manager/admin sign-off."""
    pending_list = approval_manager.list_pending()
    # Filter and format for response
    results = []
    for item in pending_list:
        results.append({
            "approval_id": item.get("approval_id"),
            "task_id": item.get("task_id"),
            "claim_id": item.get("claim_id"),
            "requester_id": item.get("requester_id"),
            "action_hash": item.get("action_hash"),
            "proposed_action": item.get("proposed_action"),
            "reasons": item.get("reasons", []),
            "risk_assessment": item.get("risk_assessment", {}),
            "status": item.get("status"),
            "created_at": item.get("created_at"),
            "expires_at": item.get("expires_at"),
        })
    return results


@router.get("/{approval_id}", tags=["Approvals"])
async def get_approval_by_id(
    approval_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Retrieve detailed state of a specific approval ticket."""
    record = approval_manager.get_approval(approval_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval ticket '{approval_id}' not found",
        )
    return {
        "approval_id": record.get("approval_id"),
        "task_id": record.get("task_id"),
        "claim_id": record.get("claim_id"),
        "requester_id": record.get("requester_id"),
        "approver_id": record.get("approver_id"),
        "approver_role": record.get("approver_role"),
        "action_hash": record.get("action_hash"),
        "proposed_action": record.get("proposed_action"),
        "reasons": record.get("reasons", []),
        "risk_assessment": record.get("risk_assessment", {}),
        "status": record.get("status"),
        "reason": record.get("reason"),
        "created_at": record.get("created_at"),
        "expires_at": record.get("expires_at"),
        "consumed_at": record.get("consumed_at"),
    }


@router.post("/{approval_id}/decide", tags=["Approvals"])
async def decide_approval(
    approval_id: str,
    request: ApprovalDecisionRequest,
    current_user: dict = Depends(require_role([UserRole.MANAGER, UserRole.ADMIN])),
) -> Dict[str, Any]:
    """Record manager approve/reject verdict on an approval request.
    Strictly prevents self-approval by requester.
    """
    record = approval_manager.get_approval(approval_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval ticket '{approval_id}' not found",
        )

    # Self-approval prevention
    if record.get("requester_id") == current_user.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Self-approval is strictly prohibited. Requester cannot approve their own action.",
        )

    verdict_clean = request.verdict.lower().strip()
    if verdict_clean not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verdict must be either 'approved' or 'rejected'",
        )

    ok, result_status = approval_manager.record_decision(
        approval_id=approval_id,
        approver_id=current_user.get("user_id"),
        approver_role=current_user.get("role"),
        verdict=verdict_clean,
        reason=request.reason or "Manager review",
    )

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot record decision: {result_status}",
        )

    return {
        "approval_id": approval_id,
        "status": result_status,
        "verdict": verdict_clean,
        "approver_id": current_user.get("user_id"),
        "reason": request.reason,
    }
