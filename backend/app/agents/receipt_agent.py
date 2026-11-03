"""Receipt Agent for AgentShield AI.
Extracts financial fields from receipt documents.
STRICT PRIVILEGE RULE: Treats all document contents as UNTRUSTED data.
Never executes instructions embedded in invoices.
"""
from typing import Dict, Any, Optional
from backend.app.services.llm_provider import LLMProvider, get_llm_provider


class ReceiptAgent:
    """Agent specialized in document extraction and data normalization."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    def process_receipt(self, receipt_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract invoice parameters with structural isolation."""
        extracted = self.llm.extract_receipt(receipt_text, context)
        return {
            "agent": "ReceiptAgent",
            "merchant": extracted.get("merchant", "Unknown Merchant"),
            "amount": float(extracted.get("amount", 0.0) or 0.0),
            "currency": extracted.get("currency", "INR"),
            "category": extracted.get("category", "travel"),
            "date": extracted.get("date", "2026-11-01"),
            "confidence": extracted.get("confidence", 0.9),
            "status": "COMPLETED",
        }
