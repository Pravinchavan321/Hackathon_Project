"""Duplicate Claim Detection Tool for AgentShield AI.
Detects recycled receipts by content hash and identical claims by parameter fingerprints.
"""
import hashlib
from typing import Dict, Any, Optional, Set
from backend.app.database import collections

_SEEN_RECEIPT_HASHES: Set[str] = set()
_SEEN_CLAIM_FINGERPRINTS: Set[str] = set()


def compute_claim_fingerprint(user_id: str, amount: float, category: str, expense_date: Optional[str] = None) -> str:
    """Generate deterministic fingerprint for identical submissions."""
    raw = f"{user_id}|{round(float(amount), 2)}|{category.lower()}|{expense_date or 'none'}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class DuplicateChecker:
    """Detects duplicate expense claims and reused receipts."""

    def __init__(self, db=None):
        self.db = db

    def check_duplicate(
        self,
        user_id: str,
        amount: float,
        category: str,
        receipt_hash: Optional[str] = None,
        expense_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Check if claim or receipt is a duplicate."""
        # 1. Check receipt content hash
        if receipt_hash:
            if self.db is not None:
                existing_receipt = self.db[collections.RECEIPTS].find_one({"file_hash": receipt_hash})
                if existing_receipt:
                    return {
                        "is_duplicate": True,
                        "match_type": "RECEIPT_CONTENT_HASH_COLLISION",
                        "matched_id": existing_receipt.get("receipt_id"),
                    }
            elif receipt_hash in _SEEN_RECEIPT_HASHES:
                return {
                    "is_duplicate": True,
                    "match_type": "RECEIPT_CONTENT_HASH_COLLISION",
                    "matched_id": receipt_hash,
                }

        # 2. Check claim fingerprint (same user, amount, category, date)
        fp = compute_claim_fingerprint(user_id, amount, category, expense_date)
        if fp in _SEEN_CLAIM_FINGERPRINTS:
            return {
                "is_duplicate": True,
                "match_type": "IDENTICAL_CLAIM_FINGERPRINT",
                "matched_id": fp,
            }

        return {
            "is_duplicate": False,
            "match_type": "NONE",
            "matched_id": None,
        }

    def record_seen(self, receipt_hash: Optional[str] = None, claim_fingerprint: Optional[str] = None):
        """Record receipt hash and claim fingerprint as seen upon successful submission."""
        if receipt_hash:
            _SEEN_RECEIPT_HASHES.add(receipt_hash)
        if claim_fingerprint:
            _SEEN_CLAIM_FINGERPRINTS.add(claim_fingerprint)
