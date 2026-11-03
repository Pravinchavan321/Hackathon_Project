# Next Session Prompt — AgentShield AI

```markdown
Resume the development of AgentShield AI from the saved repository state.

Mandatory reading order:
1. Read `docs/agent-handoff/AGENT_HANDOFF.md` completely.
2. Read `docs/agent-handoff/PROJECT_STATUS.md` and `docs/agent-handoff/PHASE_TRACKER.md`.
3. Check `docs/agent-handoff/NEXT_SESSION_PROMPT.md` for the current bounded goal.
4. Verify current test and build health by running:
   - `python -m pytest backend/tests/ -v`

Current Bounded Goal: Phase 8 — Frontend Enterprise Dashboard
Execute Phase 8 deliverables:
1. Implement Frontend API service in `frontend/src/services/api.js` with Axios client connecting to `/api/v1/auth`, `/api/v1/tasks`, `/api/v1/approvals`.
2. Implement Agent Chat & Task submission view in `frontend/src/pages/AgentChatPage.jsx`:
   - Interactive prompt input, receipt upload, live agent status pills, execution trace timeline, and policy decision badges.
3. Implement Approvals review view in `frontend/src/pages/ApprovalsPage.jsx`:
   - Pending tickets table, side-by-side action comparison, SHA-256 hash inspection, approve / reject modal with manager notes.
4. Implement Policies & Governance viewer in `frontend/src/pages/PoliciesPage.jsx`:
   - Active rules display, category limits, risk weights, fail-closed enforcement indicators.
5. Implement Evaluation Metrics view in `frontend/src/pages/EvaluationPage.jsx`:
   - Live 50-task benchmark metrics (Success Rate $\ge 85\%$, Violations = 0%, Approval Trigger = 100%, Injection Blocked = 100%).
6. Verify build cleanly via `npm run build` in `frontend/`.
7. Update `docs/agent-handoff/PHASE_TRACKER.md`, `PROJECT_STATUS.md`, `SESSION_LOG.md`, and `NEXT_SESSION_PROMPT.md` marking Phase 8 VERIFIED.
```
