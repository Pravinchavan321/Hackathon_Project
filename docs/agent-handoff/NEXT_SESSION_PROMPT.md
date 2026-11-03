# Next Session Prompt — AgentShield AI

```markdown
Resume the development of AgentShield AI from the saved repository state.

Mandatory reading order:
1. Read `docs/agent-handoff/AGENT_HANDOFF.md` completely.
2. Read `docs/agent-handoff/PROJECT_STATUS.md` and `docs/agent-handoff/PHASE_TRACKER.md`.
3. Check `docs/agent-handoff/NEXT_SESSION_PROMPT.md` for the current bounded goal.
4. Verify current test and build health by running:
   - `python -m pytest backend/tests/ -v`

Current Bounded Goal: Phase 9 — System Integration & Live WebSockets
Execute Phase 9 deliverables:
1. Implement WebSocket endpoint `/ws/tasks/{task_id}` in `backend/app/api/ws_routes.py`:
   - Connection manager tracking active client WebSocket connections per task ID.
   - Real-time event streaming: `task_started`, `agent_step` (Planner, Receipt, Validation, Execution), `governance_evaluated`, `approval_paused`, `task_resumed`, `tool_executed`, `task_completed`.
2. Wire WebSocket router in `backend/app/main.py`.
3. Author WebSocket streaming client hook in `frontend/src/hooks/useTaskStream.js` (or integrated in `AgentChatPage.jsx`) for live step streaming.
4. Author WebSocket backend test in `backend/tests/test_websocket.py` using Starlette TestClient `websocket_connect()`.
5. Run `python -m pytest backend/tests/ -v` ensuring all tests pass.
6. Verify frontend production build with `npm --prefix frontend run build`.
7. Update `docs/agent-handoff/PHASE_TRACKER.md`, `PROJECT_STATUS.md`, `SESSION_LOG.md`, and `NEXT_SESSION_PROMPT.md` marking Phase 9 VERIFIED.
```
