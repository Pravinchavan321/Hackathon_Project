"""Planner Agent for AgentShield AI.
Decomposes natural language directives into structured execution plans.
STRICT PRIVILEGE RULE: Never authorizes actions or invokes tools directly.
"""
from typing import Dict, Any, Optional
from backend.app.services.llm_provider import LLMProvider, get_llm_provider


class PlannerAgent:
    """Agent specialized in request deconstruction and subtask planning."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    def generate_plan(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Produce structured execution plan."""
        plan_output = self.llm.plan_task(input_text, context)
        return {
            "agent": "PlannerAgent",
            "objective": plan_output.get("objective", "Process expense reimbursement"),
            "task_type": plan_output.get("task_type", "expense_claim"),
            "subtasks": plan_output.get("subtasks", []),
            "status": "COMPLETED",
        }
