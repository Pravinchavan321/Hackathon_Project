# Next Session Prompt — AgentShield AI

```markdown
Resume the development of AgentShield AI from the saved repository state.

Mandatory reading order:
1. Read `docs/agent-handoff/AGENT_HANDOFF.md` completely.
2. Read `docs/agent-handoff/PROJECT_STATUS.md` and `docs/agent-handoff/PHASE_TRACKER.md`.
3. Check `docs/agent-handoff/NEXT_SESSION_PROMPT.md` for the current bounded goal.
4. Verify current test and build health by running:
   - `python -m pytest backend/tests/ -v`

Current Bounded Goal: Phase 6 — Multi-Agent System (LangGraph)
Execute Phase 6 deliverables:
1. Implement `backend/app/orchestration/state.py` (TypedDict `WorkflowState` managing task identity, input data, plan, receipt extraction, validation findings, proposed action, governance decision, approval ticket, execution result, and agent trace).
2. Implement `backend/app/services/llm_provider.py` (Abstract `LLMProvider`, `GeminiLLMProvider` using langchain-google-genai, and deterministic `MockLLMProvider` for tests).
3. Implement `backend/app/agents/planner_agent.py` (Planner Agent decomposing user instructions into pipeline subtasks).
4. Implement `backend/app/agents/receipt_agent.py` (Receipt Agent parsing receipts with untrusted content isolation).
5. Implement `backend/app/agents/validation_agent.py` (Validation Agent assessing completeness and duplicate flags).
6. Implement `backend/app/agents/execution_agent.py` (Execution Agent preparing proposed action dictionary; cannot call tools directly).
7. Implement `backend/app/orchestration/nodes.py` and `backend/app/orchestration/graph.py` (LangGraph StateGraph with conditional edges: ALLOW -> execute, DENY -> block, REQUIRE_APPROVAL -> interrupt).
8. Author `backend/tests/test_agents.py` testing the complete LangGraph flow across compliant, violating, and threshold-escalating tasks.
9. Run `python -m pytest backend/tests/ -v` ensuring all tests pass.
10. Update `docs/agent-handoff/PHASE_TRACKER.md`, `PROJECT_STATUS.md`, `SESSION_LOG.md`, and `NEXT_SESSION_PROMPT.md` marking Phase 6 VERIFIED.
```
