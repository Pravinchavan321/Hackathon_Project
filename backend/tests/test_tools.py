"""Phase 5 Verification Tests — Controlled Domain Tools & Security Boundaries."""
import pytest
from backend.app.tools.receipt_reader import ReceiptReader
from backend.app.tools.expense_validator import ExpenseValidator
from backend.app.tools.duplicate_checker import DuplicateChecker, compute_claim_fingerprint
from backend.app.tools.claim_executor import ClaimExecutor


def test_receipt_magic_byte_validation():
    """Verify receipt reader checks binary magic bytes and rejects spoofed files."""
    reader = ReceiptReader()

    # Valid PNG magic bytes
    valid_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
    ok, reason = reader.validate_file_bytes(valid_png, "image/png")
    assert ok is True
    assert reason == "VALID"

    # Valid PDF magic bytes
    valid_pdf = b"%PDF-1.4\n" + b"\x00" * 50
    ok, reason = reader.validate_file_bytes(valid_pdf, "application/pdf")
    assert ok is True
    assert reason == "VALID"

    # Spoofed file (Plain text with image/png mime)
    spoofed = b"This is just a text file with instructions."
    ok, reason = reader.validate_file_bytes(spoofed, "image/png")
    assert ok is False
    assert "MAGIC_BYTES_MISMATCH" in reason


def test_receipt_oversized_file_rejected():
    """Verify receipt reader rejects files exceeding 10MB."""
    reader = ReceiptReader()
    huge_file = b"\x89PNG\r\n\x1a\n" + b"\x00" * (11 * 1024 * 1024)
    ok, reason = reader.validate_file_bytes(huge_file, "image/png")
    assert ok is False
    assert "EXCEEDS_LIMIT" in reason


def test_expense_validator():
    """Verify validator checks positive amount, category, and receipt."""
    validator = ExpenseValidator()

    # Valid claim
    res = validator.validate_claim_data({
        "amount": 2500.0,
        "category": "travel",
        "receipt_id": "rec-123"
    })
    assert res["valid"] is True
    assert len(res["issues"]) == 0

    # Negative amount and missing receipt
    bad_res = validator.validate_claim_data({
        "amount": -50.0,
        "category": "travel",
        "receipt_id": ""
    })
    assert bad_res["valid"] is False
    assert "AMOUNT_MUST_BE_POSITIVE_NUMBER" in bad_res["issues"]
    assert "RECEIPT_ID_MISSING" in bad_res["issues"]


def test_duplicate_checker():
    """Verify duplicate checker detects duplicate receipt hashes and claim fingerprints."""
    checker = DuplicateChecker()
    user_id = "u-user-01"
    amount = 4500.0
    category = "travel"
    date = "2026-11-01"
    rec_hash = "sha256-test-hash-12345"

    # First check: Not duplicate
    res1 = checker.check_duplicate(user_id, amount, category, receipt_hash=rec_hash, expense_date=date)
    assert res1["is_duplicate"] is False

    # Record as seen
    fp = compute_claim_fingerprint(user_id, amount, category, date)
    checker.record_seen(receipt_hash=rec_hash, claim_fingerprint=fp)

    # Second check with same receipt: Duplicate!
    res2 = checker.check_duplicate(user_id, 1000.0, "meals", receipt_hash=rec_hash)
    assert res2["is_duplicate"] is True
    assert res2["match_type"] == "RECEIPT_CONTENT_HASH_COLLISION"

    # Third check with identical fingerprint: Duplicate!
    res3 = checker.check_duplicate(user_id, amount, category, expense_date=date)
    assert res3["is_duplicate"] is True
    assert res3["match_type"] == "IDENTICAL_CLAIM_FINGERPRINT"


def test_claim_executor_requires_governance_allow_ticket():
    """Hard boundary test: ClaimExecutor must reject execution without a valid ALLOW ticket."""
    executor = ClaimExecutor()
    action = {"tool": "submit_claim", "args": {"amount": 3500.0, "category": "travel"}}

    # Direct call without ticket -> PermissionError
    with pytest.raises(PermissionError) as exc_info:
        executor.execute_claim_submission(
            proposed_action=action,
            user_id="u-001",
            task_id="t-100",
            governance_ticket={"decision": "DENY"},
        )
    assert "Unauthorized tool invocation blocked" in str(exc_info.value)


def test_claim_executor_success_and_idempotency():
    """Verify ClaimExecutor runs when ticket is ALLOW and enforces idempotency on network retry."""
    executor = ClaimExecutor()
    action = {
        "tool": "submit_claim",
        "args": {
            "amount": 4200.0,
            "category": "travel",
            "receipt_id": "rec-555",
            "merchant": "Air India",
        }
    }
    ticket = {"decision": "ALLOW", "action_hash": "hash-abc123"}
    idempotency_key = "idem-unique-task-999"

    # First execution: Success
    res1 = executor.execute_claim_submission(
        proposed_action=action,
        user_id="u-001",
        task_id="t-999",
        governance_ticket=ticket,
        idempotency_key=idempotency_key,
    )
    assert res1["ok"] is True
    assert res1["status"] == "SUBMITTED"
    assert "claim_id" in res1

    # Second execution with same idempotency key (Network retry): Returns cached idempotent success
    res2 = executor.execute_claim_submission(
        proposed_action=action,
        user_id="u-001",
        task_id="t-999",
        governance_ticket=ticket,
        idempotency_key=idempotency_key,
    )
    assert res2["ok"] is True
    assert res2["status"] == "SUBMITTED_ALREADY_IDEMPOTENT"
