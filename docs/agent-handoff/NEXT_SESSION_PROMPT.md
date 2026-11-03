# Next Session Prompt — AgentShield AI

```markdown
Resume the development of AgentShield AI from the saved repository state.

Mandatory reading order:
1. Read `docs/agent-handoff/AGENT_HANDOFF.md` completely.
2. Read `docs/agent-handoff/PROJECT_STATUS.md` and `docs/agent-handoff/PHASE_TRACKER.md`.
3. Check `docs/agent-handoff/NEXT_SESSION_PROMPT.md` for the current bounded goal.
4. Verify current test and build health by running:
   - `python -m pytest backend/tests/ -v`

Current Bounded Goal: Phase 10 — 50-Task Evaluation Benchmark
Execute Phase 10 deliverables:
1. Implement evaluation module package in `eval/` with `eval/__init__.py` and `eval/run_eval.py`:
   - Loads the 50 synthetic evaluation scenarios from `data/synthetic_tasks.json`.
   - Iterates through all 50 tasks across the 4 cohorts:
     - 20 compliant claims (<= ₹5,000) $\to$ expects `ALLOW` / `SUCCEEDED`.
     - 10 threshold escalation claims (> ₹5,000) $\to$ expects `REQUIRE_APPROVAL` / paused.
     - 10 banned category claims $\to$ expects `BLOCK` / `DENIED`.
     - 10 adversarial prompt injection attacks $\to$ expects `BLOCK` / `DENIED`.
   - Computes empirical metrics according to formulas locked in `docs/METRICS.md`:
     - $SR$ (Success Rate): Target $\ge 85\%$
     - $PVR$ (Policy Violation Rate): Target $0.0\%$
     - $ATR$ (Approval Trigger Rate): Target $100.0\%$
     - $PBR$ (Prompt Injection Block Rate): Target $100.0\%$
   - Saves empirical execution summary and task-by-task results to `results/results.json`.
2. Execute benchmark runner: `python -m eval.run_eval`.
3. Verify `python -m pytest backend/tests/ -v` passes cleanly.
4. Update `docs/agent-handoff/PHASE_TRACKER.md`, `PROJECT_STATUS.md`, `SESSION_LOG.md`, and `NEXT_SESSION_PROMPT.md` marking Phase 10 VERIFIED.
```
