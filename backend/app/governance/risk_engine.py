"""Explainable Risk Assessment Engine for AgentShield AI.
Calculates transparent 0-100 risk scores with granular contributing factors.
"""
from typing import Dict, Any, List


class RiskEngine:
    """Calculates risk assessments. Supplements policy but never overrides mandatory rules."""

    THRESHOLDS = {"LOW": 30, "MEDIUM": 65}

    def assess(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any],
        policy_findings: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compute transparent risk score and contributing factors."""
        score = 10.0  # Base transaction baseline
        factors: List[str] = []

        args = action.get("args") or action.get("parameters") or {}
        amount = float(args.get("amount", 0.0) or 0.0)
        category = str(args.get("category", "")).lower()

        # 1. Amount Magnitude (0 to 35 points)
        if amount > 10000:
            score += 35.0
            factors.append("High financial value (> ₹10,000)")
        elif amount > 5000:
            score += 20.0
            factors.append("Exceeds baseline threshold (> ₹5,000)")
        elif amount > 2500:
            score += 10.0
            factors.append("Moderate expenditure (> ₹2,500)")

        # 2. Category Sensitivity (0 to 25 points)
        high_risk_categories = ["gambling", "alcohol", "gift_cards", "personal"]
        moderate_risk_categories = ["entertainment", "client_hospitality"]
        if category in high_risk_categories:
            score += 25.0
            factors.append(f"High-risk restricted category: {category}")
        elif category in moderate_risk_categories:
            score += 15.0
            factors.append(f"Discretionary expense category: {category}")

        # 3. Policy Engine Findings (0 to 25 points)
        decision = policy_findings.get("decision", "ALLOW")
        if decision == "BLOCK":
            score += 25.0
            factors.append(f"Triggered blocking policy rules: {policy_findings.get('reasons')}")
        elif decision == "ESCALATE":
            score += 15.0
            factors.append(f"Triggered escalation policy rules: {policy_findings.get('reasons')}")

        # 4. Context & Role (0 to 15 points)
        role = context.get("user_role", "EMPLOYEE")
        if role == "EMPLOYEE" and amount > 5000:
            score += 10.0
            factors.append("Standard employee proposing high-value transaction")

        score = min(100.0, max(0.0, round(score, 1)))

        if score <= self.THRESHOLDS["LOW"]:
            level = "LOW"
            recommendation = "ALLOW"
        elif score <= self.THRESHOLDS["MEDIUM"]:
            level = "MEDIUM"
            recommendation = "REQUIRE_HUMAN_APPROVAL"
        else:
            level = "HIGH"
            recommendation = "REQUIRE_EXECUTIVE_APPROVAL"

        return {
            "score": score,
            "level": level,
            "factors": factors,
            "recommended_action": recommendation,
        }
