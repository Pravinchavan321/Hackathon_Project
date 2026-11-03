# Next Session Prompt — AgentShield AI

```markdown
Resume the development of AgentShield AI from the saved repository state.

Mandatory reading order:
1. Read `docs/agent-handoff/AGENT_HANDOFF.md` completely.
2. Read `docs/agent-handoff/PROJECT_STATUS.md` and `docs/agent-handoff/PHASE_TRACKER.md`.
3. Check `docs/agent-handoff/NEXT_SESSION_PROMPT.md` for the current bounded goal.
4. Verify current test and build health by running:
   - `python -m pytest backend/tests/ -v`

Current Bounded Goal: Phase 7 — Human Approval & State Pause/Resume API
Execute Phase 7 deliverables:
1. Implement Approval REST endpoints in `backend/app/api/approval_routes.py`:
   - `GET /api/v1/approvals/pending` (retrieves pending approval requests for manager/admin).
   - `GET /api/v1/approvals/{approval_id}` (retrieves specific approval with exact proposed action & reasons).
   - `POST /api/v1/approvals/{approval_id}/decide` (records manager approve/reject verdict with comment).
2. Implement Task execution & resume REST endpoints in `backend/app/api/task_routes.py`:
   - `POST /api/v1/tasks/run` (initiates LangGraph agent workflow; handles direct completion or approval pause).
   - `POST /api/v1/tasks/{task_id}/resume` (resumes paused task after manager approval using `resume_workflow`).
   - `GET /api/v1/tasks/{task_id}` (fetches task status and agent trace).
3. Register routes in `backend/app/main.py`.
4. Author `backend/tests/test_api_approvals.py` testing the complete HTTP flow: initiate task -> receive interrupt status -> query pending approvals -> submit approval -> resume task -> verify SUCCEEDED status.
5. Run `python -m pytest backend/tests/ -v` ensuring all tests pass.
6. Update `docs/agent-handoff/PHASE_TRACKER.md`, `PROJECT_STATUS.md`, `SESSION_LOG.md`, and `NEXT_SESSION_PROMPT.md` marking Phase 7 VERIFIED.
```
