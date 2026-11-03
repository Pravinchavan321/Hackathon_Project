"""MongoDB Index Definitions for AgentShield AI.
Enforces unique constraints, performance lookups, and duplicate prevention.
"""
import logging
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database
from backend.app.database import collections

logger = logging.getLogger(__name__)


def ensure_indexes(db: Database) -> dict:
    """Create all required indexes across collections.
    Returns dictionary of results per collection.
    """
    results = {}
    if db is None:
        logger.warning("Database not provided; skipping index creation.")
        return results

    try:
        # 1. users: unique lowercase email, unique user_id
        db[collections.USERS].create_index([("email", ASCENDING)], unique=True, name="idx_user_email_unique")
        db[collections.USERS].create_index([("user_id", ASCENDING)], unique=True, name="idx_user_id_unique")
        db[collections.USERS].create_index([("role", ASCENDING), ("status", ASCENDING)], name="idx_user_role_status")
        results[collections.USERS] = "OK"

        # 2. expense_claims: unique claim_id, user scoping, idempotency
        db[collections.EXPENSE_CLAIMS].create_index([("claim_id", ASCENDING)], unique=True, name="idx_claim_id_unique")
        db[collections.EXPENSE_CLAIMS].create_index([("user_id", ASCENDING), ("status", ASCENDING)], name="idx_claim_user_status")
        db[collections.EXPENSE_CLAIMS].create_index([("user_id", ASCENDING), ("created_at", DESCENDING)], name="idx_claim_user_created")
        db[collections.EXPENSE_CLAIMS].create_index([("idempotency_key", ASCENDING)], unique=True, sparse=True, name="idx_claim_idempotency")
        db[collections.EXPENSE_CLAIMS].create_index([("task_id", ASCENDING)], name="idx_claim_task_id")
        results[collections.EXPENSE_CLAIMS] = "OK"

        # 3. receipts: unique receipt_id, file hash lookup
        db[collections.RECEIPTS].create_index([("receipt_id", ASCENDING)], unique=True, name="idx_receipt_id_unique")
        db[collections.RECEIPTS].create_index([("owner_id", ASCENDING)], name="idx_receipt_owner")
        db[collections.RECEIPTS].create_index([("file_hash", ASCENDING)], name="idx_receipt_hash")
        results[collections.RECEIPTS] = "OK"

        # 4. policies: unique policy_id, version compound
        db[collections.POLICIES].create_index([("policy_id", ASCENDING)], unique=True, name="idx_policy_id_unique")
        db[collections.POLICIES].create_index([("name", ASCENDING), ("version", ASCENDING)], unique=True, name="idx_policy_version_unique")
        db[collections.POLICIES].create_index([("active", ASCENDING)], name="idx_policy_active")
        results[collections.POLICIES] = "OK"

        # 5. agent_tasks: unique task_id, status queries
        db[collections.AGENT_TASKS].create_index([("task_id", ASCENDING)], unique=True, name="idx_task_id_unique")
        db[collections.AGENT_TASKS].create_index([("requester_id", ASCENDING), ("status", ASCENDING)], name="idx_task_requester_status")
        db[collections.AGENT_TASKS].create_index([("status", ASCENDING), ("created_at", DESCENDING)], name="idx_task_status_created")
        results[collections.AGENT_TASKS] = "OK"

        # 6. tool_executions: unique execution_id, idempotency key
        db[collections.TOOL_EXECUTIONS].create_index([("execution_id", ASCENDING)], unique=True, name="idx_exec_id_unique")
        db[collections.TOOL_EXECUTIONS].create_index([("idempotency_key", ASCENDING)], unique=True, sparse=True, name="idx_exec_idempotency")
        db[collections.TOOL_EXECUTIONS].create_index([("task_id", ASCENDING)], name="idx_exec_task")
        results[collections.TOOL_EXECUTIONS] = "OK"

        # 7. approvals: unique approval_id, expiry search
        db[collections.APPROVALS].create_index([("approval_id", ASCENDING)], unique=True, name="idx_approval_id_unique")
        db[collections.APPROVALS].create_index([("task_id", ASCENDING), ("status", ASCENDING)], name="idx_approval_task_status")
        db[collections.APPROVALS].create_index([("status", ASCENDING), ("expires_at", ASCENDING)], name="idx_approval_status_expiry")
        results[collections.APPROVALS] = "OK"

        # 8. audit_logs: fast queries by correlation, actor, task
        db[collections.AUDIT_LOGS].create_index([("event_id", ASCENDING)], unique=True, name="idx_audit_id_unique")
        db[collections.AUDIT_LOGS].create_index([("task_id", ASCENDING), ("timestamp", DESCENDING)], name="idx_audit_task_time")
        db[collections.AUDIT_LOGS].create_index([("claim_id", ASCENDING), ("timestamp", DESCENDING)], name="idx_audit_claim_time")
        db[collections.AUDIT_LOGS].create_index([("actor_id", ASCENDING), ("timestamp", DESCENDING)], name="idx_audit_actor_time")
        db[collections.AUDIT_LOGS].create_index([("correlation_id", ASCENDING)], name="idx_audit_correlation")
        results[collections.AUDIT_LOGS] = "OK"

        # 9. evaluations: run_id and case_id
        db[collections.EVALUATIONS].create_index([("run_id", ASCENDING), ("case_id", ASCENDING)], name="idx_eval_run_case")
        results[collections.EVALUATIONS] = "OK"

        logger.info("Successfully verified all MongoDB indexes.")
    except Exception as e:
        logger.error("Error creating MongoDB indexes: %s", str(e))
        results["error"] = str(e)

    return results
