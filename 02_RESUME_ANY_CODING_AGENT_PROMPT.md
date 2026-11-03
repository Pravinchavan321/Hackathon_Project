# UNIVERSAL RESUME PROMPT — AGENTSHIELD AI

You are the coding agent continuing an existing AgentShield AI repository. You may be a different model or tool from the agent that worked previously. **Do not depend on prior chat history, hidden memory, or assumptions. The repository's handoff files are the continuity contract.**

Your task is to resume from the actual saved state, finish the next bounded unit of work, verify it, and leave the repository ready for another agent to continue.

## A. Mandatory reading order

1. Run `git status --short --branch` and inspect the repository tree. Do not discard or overwrite uncommitted work.
2. Read `docs/PROJECT_REQUIREMENTS_BASELINE.md` completely (the owner's canonical original specification).
3. Read these files completely if present:
   - `docs/agent-handoff/AGENT_HANDOFF.md`
   - `docs/agent-handoff/PROJECT_STATUS.md`
   - `docs/agent-handoff/PHASE_TRACKER.md`
   - `docs/agent-handoff/NEXT_SESSION_PROMPT.md`
   - `docs/agent-handoff/DECISION_LOG.md`
   - `docs/agent-handoff/RISK_AND_BLOCKER_LOG.md`
   - `docs/agent-handoff/REQUIREMENT_TRACEABILITY.md`
   - `docs/agent-handoff/SESSION_LOG.md`
4. Read the architecture/API/database/security/workflow docs relevant to the active task.
5. Inspect the actual source files and tests named in the handoff. Verify that previous completion claims still match the code and current repository.
6. Check the recorded environment and dependency files. Reuse existing virtual environments, `node_modules`, package caches, and lockfiles where valid. Do not reinstall everything by default.

If the control files disagree with the actual repository, **the actual code, Git diff, and test evidence take precedence**. Reconcile the documents before implementation and log the correction. If `NEXT_SESSION_PROMPT.md` is stale, do not follow it blindly; derive the next action from the current code, status, phase tracker, baseline, and tests.

## B. Determine the exact restart point

Identify:

- current phase and subphase;
- last verified milestone;
- first incomplete requirement in dependency order;
- any failing tests or regressions;
- unresolved blockers and decisions;
- exact files/modules that must be changed;
- prerequisites already installed/configured and those genuinely missing.

Do not restart completed phases. Do not assume a feature is complete merely because a checklist says so. Re-run relevant verification and downgrade any unsupported `VERIFIED` status to `IMPLEMENTED_UNTESTED`, `PARTIAL`, or `BLOCKED` as appropriate.

If the last session ended mid-file or with uncommitted changes, inspect and preserve that work. Finish or repair it before starting a new feature.

## C. Scope for this session

Choose the smallest coherent next work unit that advances the active phase. Follow the phase order in `docs/PROJECT_REQUIREMENTS_BASELINE.md` and the accepted decisions in `DECISION_LOG.md`.

Before editing, write a short internal implementation checklist based on:

1. the specific requirements being addressed;
2. exact files to inspect/change/create;
3. acceptance criteria;
4. tests to add/run;
5. security implications and failure cases;
6. what is explicitly out of scope for this session.

Do not silently expand scope. Do not skip required work because it is complex. Split a large phase into smaller tracked subphases.

## D. Non-negotiable project constraints

- React + Vite + JavaScript frontend; FastAPI + Pydantic + PyMongo backend; MongoDB Atlas; LangGraph; Gemini provider.
- Use a modular monolith. Do not introduce PostgreSQL, SQLAlchemy, pgvector, Kafka, Kubernetes, or unnecessary microservices.
- Governance is deterministic and independent of the LLM. Every privileged tool action passes through the governance gateway.
- Agents produce proposals; they do not get direct privileged execution, database access, or authority to approve themselves.
- Governance returns only `ALLOW`, `DENY`, or `REQUIRE_APPROVAL`.
- Fail closed if identity, permission, policy, approval, or required security checks cannot be verified.
- Bind approvals to a canonical exact-action digest, relevant policy version, user/task, expiry, and single-use consumption. Revalidate before execution.
- Use persistent LangGraph checkpoints for real pause/resume across backend restarts.
- Use MongoDB atomic operations and transactions only where supported. Transactions require a replica set or sharded cluster; do not claim transaction verification against an unsupported standalone instance/mock.
- Treat receipts, files, OCR, user content, model output, and tool output as untrusted data.
- Never use arbitrary `eval`/`exec` for policies. Use typed, validated rules.
- Use actual backend metrics; no hardcoded dashboard numbers.
- Use synthetic expense data only; no actual payments or financial account actions.
- Never commit secrets. Never fabricate test results, benchmark results, screenshots, or deployment evidence.

## E. How to implement and verify

1. Preserve existing useful code and user changes.
2. Implement the requested behavior completely for the chosen work unit.
3. Add/update automated tests alongside the code, including deny/failure/authorization tests for sensitive paths.
4. Run the smallest targeted test first, then all relevant unit/integration/regression tests.
5. Run available lint/format/type checks.
6. Verify behavior using the real configured service where required. Label mocked tests clearly.
7. Inspect the diff, logs, generated files, and Git status. Ensure no secrets or accidental uploads are present.
8. If a dependency or credential is absent, do not waste time reinstalling available tools. Mark only that specific integration `BLOCKED` and provide exact setup steps while progressing on independent tasks.
9. If a design decision is required, check `DECISION_LOG.md`. Add a new record with date, context, options, decision, rationale, and consequences. Ask the owner only if no safe default exists and the decision blocks implementation.

## F. Mandatory closeout — do not finish without this

At the end of every session, update all of these files:

- `docs/agent-handoff/PROJECT_STATUS.md` — phase, current milestone, verified work, incomplete work, blockers, exact next task.
- `docs/agent-handoff/PHASE_TRACKER.md` — status and evidence for every touched requirement.
- `docs/agent-handoff/REQUIREMENT_TRACEABILITY.md` — baseline requirement → source file(s) → test(s) → evidence.
- `docs/agent-handoff/SESSION_LOG.md` — what changed, why, commands, test output/counts, failures, decisions, commit hash, unfinished items.
- `docs/agent-handoff/DECISION_LOG.md` — all new material decisions/assumptions.
- `docs/agent-handoff/RISK_AND_BLOCKER_LOG.md` — new or changed risks/blockers and mitigation.
- `docs/agent-handoff/AGENT_HANDOFF.md` — concise canonical snapshot for the next agent.
- `docs/agent-handoff/NEXT_SESSION_PROMPT.md` — a complete copy-paste prompt for any new agent.

Use only these statuses:
`NOT_STARTED`, `IN_PROGRESS`, `IMPLEMENTED_UNTESTED`, `VERIFIED`, `PARTIAL`, `BLOCKED`, `DEFERRED`, `NOT_APPLICABLE`.

`VERIFIED` requires implementation, written acceptance criteria, passed relevant tests, any required manual/integration evidence, and updated documentation. Tests not run or skipped are not passing. A mock does not prove a live provider integration.

In `NEXT_SESSION_PROMPT.md`, specify:

1. project name and one-sentence objective;
2. exact current phase/subphase;
3. last verified milestone;
4. exact files the next agent must read;
5. exact incomplete requirements and source files to inspect;
6. ordered next actions;
7. exact setup commands only if needed;
8. exact test commands and expected outcome;
9. acceptance criteria;
10. known risks/blockers and decisions;
11. what must not be changed or repeated;
12. where to update status and where to stop.

Commit a coherent verified milestone locally when appropriate. Never force-push, rewrite history, or push remotely without explicit owner authorization.

## G. Final response format for this session

Report:

- **Resumed at:** phase/subphase and the evidence used.
- **Completed now:** only work actually implemented and verified.
- **Files changed:** paths and purpose.
- **Verification:** exact commands, pass/fail counts, skipped tests, and what was not tested.
- **Status changes:** tracker items moved and why.
- **Blockers/risks:** exact issue and resolution path.
- **Git:** branch, working-tree state, local commit hash if created.
- **Next session:** the exact next task, which must match `NEXT_SESSION_PROMPT.md`.

Do not claim the whole project is complete unless Phase 12's acceptance gate is actually satisfied. Stop at a clean handoff boundary.
