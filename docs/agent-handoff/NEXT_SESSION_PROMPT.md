# Next Session Prompt — AgentShield AI

```markdown
Resume the development of AgentShield AI from the saved repository state.

Mandatory reading order:
1. Read `docs/agent-handoff/AGENT_HANDOFF.md` completely.
2. Read `docs/agent-handoff/PROJECT_STATUS.md` and `docs/agent-handoff/PHASE_TRACKER.md`.
3. Check `docs/agent-handoff/NEXT_SESSION_PROMPT.md` for the current bounded goal.
4. Verify current test and build health by running:
   - `python -m pytest backend/tests/ -v`

Current Bounded Goal: Phase 12 — Final Hackathon Readiness & Pitch Pack
Execute Phase 12 deliverables:
1. Polish root `README.md` with:
   - High-level architecture and Mermaid flowchart
   - Core differentiators (LLM proposes, deterministic governance enforces)
   - Quick-start guide (`docker compose up -d` or local instructions)
   - Test suite and benchmark command execution (`pytest` and `eval.run_eval`)
   - Links to all documentation specs in `docs/`
2. Validate the 3-minute hackathon demo rehearsal script in `docs/demo-script.md` against the working React frontend and FastAPI backend.
3. Perform final verification check across all 12 phases (`pytest`, `run_eval`, `npm run build`, `docker compose config`).
4. Update `docs/agent-handoff/PHASE_TRACKER.md`, `PROJECT_STATUS.md`, `SESSION_LOG.md`, and `NEXT_SESSION_PROMPT.md` marking Phase 12 and the entire project VERIFIED (100%).
```
