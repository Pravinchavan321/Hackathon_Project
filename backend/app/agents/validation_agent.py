"""Validation Agent for AgentShield AI.
Assesses cross-field consistency and duplicate indicators.
STRICT PRIVILEGE RULE: Reports factual findings only; does not make authorization decisions.
"""
from typing import Dict, Any, Optional
from backend.app.services.llm_provider import LLMProvider, get_llm_provider
from backend.app.tools.duplicate_checker import DuplicateChecker


class ValidationAgent:
    """Agent specialized in consistency verification and duplicate detection."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None, duplicate_checker: Optional[DuplicateChecker] = None):
        self.llm = llm_provider or get_llm_provider()
        self.duplicate_checker = duplicate_checker or DuplicateChecker()

    def validate(
        self,
        claim_data: Dict[str, Any],
        receipt_data: Dict[str, Any],
        user_id: str,
        receipt_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform cross-validation and duplicate detection."""
        # 1. Structural consistency
        llm_findings = self.llm.validate_expense(claim_data, receipt_data)

        # 2. Duplicate checking
        amount = float(claim_data.get("amount", 0.0) or receipt_data.get("amount", 0.0))
        category = str(claim_data.get("category") or receipt_data.get("category", "travel"))
        date = claim_data.get("expense_date") or receipt_data.get("date")

        dup_res = self.duplicate_checker.check_duplicate(
            user_id=user_id,
            amount=amount,
            category=category,
            receipt_hash=receipt_hash,
            expense_date=date,
        )

        return {
            "agent": "ValidationAgent",
            "is_valid": llm_findings.get("valid", True) and not dup_res.get("is_duplicate", False),
            "duplicate_detected": dup_res.get("is_duplicate", False),
            "duplicate_match_type": dup_res.get("match_type"),
            "issues": llm_findings.get("issues", []),
            "warnings": llm_findings.get("warnings", []),
            "status": "COMPLETED",
        }
