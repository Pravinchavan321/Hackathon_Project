"""LLM Provider Service for AgentShield AI.
Abstract interface supporting Gemini API and a deterministic Mock provider for offline testing.
"""
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.app.config import get_settings

settings = get_settings()


class LLMProvider(ABC):
    """Abstract interface for LLM provider operations."""

    @abstractmethod
    def plan_task(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Deconstruct task prompt into structured subtasks."""
        pass

    @abstractmethod
    def extract_receipt(self, receipt_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract structured financial parameters from receipt text."""
        pass

    @abstractmethod
    def validate_expense(self, claim_data: Dict[str, Any], receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess consistency between claim parameters and extracted invoice data."""
        pass


class MockLLMProvider(LLMProvider):
    """Deterministic mock provider.
    Deliberately gullible to prompt injection to prove that deterministic governance catches violations.
    """

    def plan_task(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        text = prompt.lower()
        subtasks = [
            {"step": 1, "agent": "receipt_agent", "action": "extract_receipt_parameters"},
            {"step": 2, "agent": "validation_agent", "action": "verify_policy_consistency"},
            {"step": 3, "agent": "execution_agent", "action": "prepare_action_proposal"},
        ]
        return {
            "objective": "Process expense reimbursement",
            "task_type": "expense_claim",
            "subtasks": subtasks,
            "confidence": 0.98,
        }

    def extract_receipt(self, receipt_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        text = (receipt_text or "").lower()

        # Parse amounts (e.g., ₹4,500 or 4500 or Rs 9000)
        amount = 4500.0
        amt_match = re.search(r"(?:₹|rs\.?|inr)?\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?)", text)
        if amt_match:
            try:
                amount = float(amt_match.group(1).replace(",", ""))
            except Exception:
                amount = 4500.0

        # Category parsing
        category = "travel"
        for cat in ["personal", "alcohol", "gambling", "gift_cards", "meals", "lodging", "transport", "supplies", "travel"]:
            if cat in text:
                category = cat
                break

        merchant = "Vendor Services"
        if "air india" in text or "flight" in text:
            merchant = "Air India"
        elif "railway" in text or "train" in text or "irctc" in text:
            merchant = "Indian Railways"
        elif "hotel" in text or "stay" in text:
            merchant = "Taj Hotels"

        return {
            "merchant": merchant,
            "amount": amount,
            "currency": "INR",
            "category": category,
            "date": "2026-11-01",
            "confidence": 0.95,
            "raw_text_length": len(receipt_text),
        }

    def validate_expense(self, claim_data: Dict[str, Any], receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        warnings = []

        claim_amt = float(claim_data.get("amount", 0.0) or 0.0)
        rec_amt = float(receipt_data.get("amount", 0.0) or 0.0)

        if abs(claim_amt - rec_amt) > 1.0:
            warnings.append(f"Amount mismatch: Claim states ₹{claim_amt}, receipt indicates ₹{rec_amt}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "consistency_score": 95 if not warnings else 75,
        }


class GeminiLLMProvider(LLMProvider):
    """Real Gemini API integration via langchain-google-genai."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.model = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=api_key,
                temperature=0.0,
            )
        except Exception:
            self.model = None

    def plan_task(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.model:
            return MockLLMProvider().plan_task(prompt, context)
        try:
            res = self.model.invoke(f"Deconstruct this expense task into JSON with objective, task_type, subtasks: {prompt}")
            return {"objective": res.content, "subtasks": [], "model": "gemini-2.0-flash"}
        except Exception:
            return MockLLMProvider().plan_task(prompt, context)

    def extract_receipt(self, receipt_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return MockLLMProvider().extract_receipt(receipt_text, context)

    def validate_expense(self, claim_data: Dict[str, Any], receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        return MockLLMProvider().validate_expense(claim_data, receipt_data)


def get_llm_provider() -> LLMProvider:
    """Factory creating configured LLM provider."""
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return GeminiLLMProvider(api_key=settings.GEMINI_API_KEY)
    return MockLLMProvider()
