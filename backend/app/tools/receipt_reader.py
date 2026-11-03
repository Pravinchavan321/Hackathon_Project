"""Receipt Storage and Document Ingestion Tool for AgentShield AI.
Validates file binary magic bytes, enforces size limits, and computes SHA-256 content hashes.
Treats all file contents as UNTRUSTED data.
"""
import hashlib
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from backend.app.config import get_settings
from backend.app.database import collections

settings = get_settings()

# Allowed signatures: mime -> magic byte prefix
MAGIC_SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "application/pdf": [b"%PDF"],
    "image/webp": [b"RIFF"],
}

_MEMORY_RECEIPTS: Dict[str, Dict[str, Any]] = {}


class ReceiptReader:
    """Safe document processor that ingests and validates receipt uploads."""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(self, db=None, storage_dir: Optional[str] = None):
        self.db = db
        self.storage_dir = storage_dir or settings.LOCAL_STORAGE_PATH
        os.makedirs(self.storage_dir, exist_ok=True)

    def validate_file_bytes(self, file_bytes: bytes, declared_mime: str) -> Tuple[bool, str]:
        """Validate file size and magic bytes against declared MIME type."""
        if not file_bytes:
            return False, "EMPTY_FILE"

        if len(file_bytes) > self.MAX_FILE_SIZE:
            return False, f"FILE_SIZE_EXCEEDS_LIMIT (Max {self.MAX_FILE_SIZE // (1024*1024)}MB)"

        mime = declared_mime.lower().strip()
        if mime not in MAGIC_SIGNATURES:
            return False, f"UNSUPPORTED_MIME_TYPE: {declared_mime}"

        valid_signature = False
        for sig in MAGIC_SIGNATURES[mime]:
            if file_bytes.startswith(sig):
                valid_signature = True
                break

        if not valid_signature:
            return False, "INVALID_FILE_SIGNATURE_MAGIC_BYTES_MISMATCH"

        return True, "VALID"

    def store_receipt(
        self,
        file_bytes: bytes,
        declared_mime: str,
        owner_id: str,
        original_filename: str = "receipt.png",
    ) -> Dict[str, Any]:
        """Ingest, hash, and store receipt file outside public web root."""
        is_valid, reason = self.validate_file_bytes(file_bytes, declared_mime)
        if not is_valid:
            raise ValueError(f"Receipt validation failed: {reason}")

        receipt_id = "rec-" + uuid.uuid4().hex[:8]
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        storage_key = os.path.join(self.storage_dir, f"{receipt_id}.bin")

        # Save binary file securely
        with open(storage_key, "wb") as f:
            f.write(file_bytes)

        now = datetime.utcnow()
        doc = {
            "receipt_id": receipt_id,
            "owner_id": owner_id,
            "original_filename": original_filename,
            "storage_key": storage_key,
            "content_type": declared_mime,
            "file_size": len(file_bytes),
            "file_hash": file_hash,
            "created_at": now,
        }

        if self.db is not None:
            self.db[collections.RECEIPTS].insert_one(doc)
        _MEMORY_RECEIPTS[receipt_id] = doc

        return doc

    def get_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve receipt metadata by ID."""
        if self.db is not None:
            return self.db[collections.RECEIPTS].find_one({"receipt_id": receipt_id})
        return _MEMORY_RECEIPTS.get(receipt_id)
