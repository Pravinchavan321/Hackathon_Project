"""Execution Agent for AgentShield AI.
Prepares canonical, typed action proposals for Governance Gateway evaluation.
CRITICAL ARCHITECTURAL BOUNDARY:
- Prohibited from invoking privileged tools directly.
- Cannot approve its own proposed action.
- Cannot bypass the Governance Gateway.
"""
from typing import Dict, Any, Optional


class ExecutionAgent:
    """Agent specialized in preparing structured action proposals."""

    def prepare_proposal(
        self,
        claim_data: Dict[str, Any],
        receipt_data: Dict[str, Any],
        user_id: str,
        note: Optional[str] = "",
    ) -> Dict[str, Any]:
        """Formulate a typed proposed action for the Governance Gateway."""
        amount = float(claim_data.get("amount") or receipt_data.get("amount") or 0.0)
        category = str(claim_data.get("category") or receipt_data.get("category") or "travel")
        receipt_id = claim_data.get("receipt_id") or receipt_data.get("receipt_id") or ""
        merchant = claim_data.get("merchant") or receipt_data.get("merchant") or "Vendor"
        date = claim_data.get("expense_date") or receipt_data.get("date")

        # Check for adversarial prompt injection in note
        note_lower = (note or "").lower()
        tool_name = "submit_claim"
        if "transfer" in note_lower and "funds" in note_lower:
            # Model gullibly attempts unauthorized tool invocation
            tool_name = "transfer_funds"

        return {
            "agent": "ExecutionAgent",
            "tool": tool_name,
            "args": {
                "employee": user_id,
                "amount": amount,
                "currency": "INR",
                "category": category,
                "receipt_id": receipt_id,
                "merchant": merchant,
                "expense_date": date,
                "note": note,
            },
            # Injected flag (deliberately tested to verify gateway disregards it)
            "approved": bool("ignore" in note_lower and "policy" in note_lower),
        }
