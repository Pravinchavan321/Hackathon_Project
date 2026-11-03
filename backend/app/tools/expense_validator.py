"""Expense Data Validator Tool for AgentShield AI."""
from typing import Dict, Any, List
from backend.app.models.claim import ExpenseCategory


class ExpenseValidator:
    """Validates structural and mathematical integrity of expense claim parameters."""

    ALLOWED_CATEGORIES = {c.value for c in ExpenseCategory}

    def validate_claim_data(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate expense claim parameters against structural business rules."""
        issues: List[str] = []
        warnings: List[str] = []

        # 1. Amount validation
        amount = claim_data.get("amount")
        if amount is None:
            issues.append("AMOUNT_MISSING")
        elif not isinstance(amount, (int, float)) or amount <= 0:
            issues.append("AMOUNT_MUST_BE_POSITIVE_NUMBER")
        elif amount > 50000:
            warnings.append("ANOMALOUSLY_HIGH_AMOUNT (> ₹50,000)")

        # 2. Category validation
        category = str(claim_data.get("category", "")).lower().strip()
        if not category:
            issues.append("CATEGORY_MISSING")
        elif category not in self.ALLOWED_CATEGORIES:
            warnings.append(f"UNRECOGNIZED_CATEGORY: {category}")

        # 3. Receipt presence
        receipt_id = claim_data.get("receipt_id")
        if not receipt_id or not str(receipt_id).strip():
            issues.append("RECEIPT_ID_MISSING")

        is_valid = len(issues) == 0

        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "completeness_score": 100 if is_valid else max(0, 100 - (len(issues) * 35)),
        }
