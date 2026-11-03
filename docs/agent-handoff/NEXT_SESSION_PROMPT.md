# Next Session Prompt — AgentShield AI

```markdown
Resume the development of AgentShield AI from the saved repository state.

Mandatory reading order:
1. Read `docs/agent-handoff/AGENT_HANDOFF.md` completely.
2. Read `docs/agent-handoff/PROJECT_STATUS.md` and `docs/agent-handoff/PHASE_TRACKER.md`.
3. Check `docs/agent-handoff/NEXT_SESSION_PROMPT.md` for the current bounded goal.
4. Verify current test and build health by running:
   - `python -m pytest backend/tests/ -v`

Current Bounded Goal: Phase 11 — Deployment & Containerization
Execute Phase 11 deliverables:
1. Implement production `frontend/Dockerfile` multi-stage build (Node 18 build stage + Nginx Alpine runtime stage) and `frontend/nginx.conf` reverse proxy routing `/api/` and `/ws/` to backend.
2. Optimize root `docker-compose.yml` orchestrating MongoDB (with healthcheck), FastAPI backend, and React frontend services on dedicated network with health probes.
3. Validate container configurations and deployment instructions in `docs/deployment-guide.md`.
4. Run health check validation and test suite: `python -m pytest backend/tests/ -v`.
5. Update `docs/agent-handoff/PHASE_TRACKER.md`, `PROJECT_STATUS.md`, `SESSION_LOG.md`, and `NEXT_SESSION_PROMPT.md` marking Phase 11 VERIFIED.
```
