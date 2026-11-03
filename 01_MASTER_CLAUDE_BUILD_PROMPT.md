# MASTER PROMPT — BUILD AGENTSHIELD AI IN CONTROLLED PHASES

You are Claude Code acting as a senior software architect, full-stack engineer, AI/agent engineer, application security engineer, database engineer, QA engineer, and DevOps engineer. Your task is to build **AgentShield AI**, a real, modular, testable, policy-governed multi-agent application.

This is a long-running repository project. Work in phases. Do not try to generate the complete system in one response or one coding session. The deliverable is the actual working repository, not a wall of code in chat.

---

## 1. Read the specification and establish the source of truth

Before changing code:

1. Inspect the current working directory, repository tree, Git branch, `git status`, existing README, package files, environment files, tests, and current implementation.
2. Read `docs/PROJECT_REQUIREMENTS_BASELINE.md` completely. It is the owner's canonical functional specification. It contains the identity, objectives, prescribed stack, architecture, simulated expense workflow, agents, governance, database collections, API list, frontend pages, security requirements, testing, deployment, documentation, and original 12-phase plan.
3. Do not assume the repository is empty. Preserve useful existing work. Never overwrite user changes or delete files just to make the tree match a proposed structure.
4. If the baseline file is absent, stop implementation and report that the required specification is missing. Do not reconstruct it from memory.
5. Treat the following as the authority order:
   - Owner's `docs/PROJECT_REQUIREMENTS_BASELINE.md` for requested behavior and scope.
   - Accepted technical decisions in `docs/agent-handoff/DECISION_LOG.md` for ambiguities resolved during development.
   - Current code and passing tests for what is actually implemented.
   - Status/checklist documents for navigation only; verify their claims against the repository.
6. If two requirements conflict, record the conflict in the decision log and resolve it conservatively. Ask the owner only when a decision genuinely blocks safe implementation. For non-blocking gaps, propose a clearly labelled default, record it, and proceed.

## 2. Product outcome

Build AgentShield AI: **Autonomous Intelligence. Governed Execution. Trusted Outcomes.**

The platform must let authenticated users submit multi-step tasks, let specialized agents plan and prepare work, and let an independent deterministic governance layer decide whether sensitive operations are allowed. High-risk or policy-sensitive operations require an authorized human approval. The system must log decisions and execution outcomes and calculate dashboard/evaluation metrics from real stored events.

The first demonstration is a **simulated expense-claim workflow using synthetic company data and synthetic receipts**. No real payment, bank transfer, or financial-account integration is required or permitted for the demo.

Core principle:

> AI agents may decide how to prepare a task, but they must never decide whether they are authorized to perform a sensitive operation. Authorization belongs to the independent governance engine.

The project must remain generic and reusable. Do not hard-code the product as a university-only or expense-only platform. Keep the initial expense workflow as a domain module/demo.

## 3. Non-negotiable technology constraints

Use the baseline stack unless a real compatibility blocker is documented:

- Frontend: React, Vite, JavaScript, Tailwind CSS, shadcn/ui, Axios, React Router, Recharts.
- Backend: Python, FastAPI, Pydantic, PyMongo, JWT-based auth, WebSockets.
- Agents: LangGraph; LangChain only where it adds value; Gemini as the primary model provider.
- Database: MongoDB Atlas + PyMongo.
- Testing: Pytest, FastAPI TestClient/httpx, Postman for manual checks; frontend tests where useful.
- Deployment: Docker/Compose and an appropriate frontend/backend host.

Hard constraints:

- Do not introduce PostgreSQL, SQLAlchemy, pgvector, Kafka, Kubernetes, or microservices without a documented, compelling reason and owner agreement.
- Use a modular monolith first. Keep boundaries clean enough that a separate service could be extracted later, but do not distribute the MVP unnecessarily.
- Redis, object storage, LangSmith, and vector search are optional. Do not make the core application depend on optional infrastructure.
- Use PyMongo, not an ORM.
- Never commit API keys, JWT secrets, database passwords, refresh tokens, or real receipts.
- Check installed versions before installing anything. Reuse a valid environment and lockfiles. Do not repeatedly download tools or packages each session.
- Verify current official package documentation and compatibility before selecting dependency versions. Pin successful versions and commit lockfiles.

## 4. Critical architecture and security rules

### 4.1 Governance is a hard authorization boundary

Implement the governance engine as deterministic application code, not an LLM prompt and not an LLM opinion. It can live inside the modular monolith, but it must be an independent authorization boundary from the agents and model provider.

- LLMs and agents can produce **proposed actions** only.
- Agents must not receive direct access to the MongoDB client, privileged executor functions, raw credentials, or unrestricted tool implementations.
- No agent may call a sensitive tool directly.
- Every privileged operation must pass through one `GovernanceGateway` (or equivalently named single enforcement boundary).
- The gateway must authenticate the initiating user, validate a server-issued agent identity/capability, verify role permissions, evaluate active policies, evaluate risk, validate an approval when required, write the decision/audit event, and only then return an authorized execution capability/result.
- The only governance decision values are `ALLOW`, `DENY`, and `REQUIRE_APPROVAL`. Return structured reason codes and explanations in addition to the decision.
- Fail closed: if policy data, permission data, approval validation, or a required security dependency cannot be checked, do not execute the sensitive operation.
- Never trust an agent-supplied `role`, `user_id`, `agent_id`, `tenant_id`, `approved` flag, risk level, or policy result. Resolve security identity from authenticated server-side context.
- Do not expose an unrestricted public endpoint that lets a client or agent obtain arbitrary authorization. `/governance/evaluate` may exist for controlled admin/testing purposes, but actual execution must call the internal gateway. Protect any public diagnostic route with appropriate authorization and strict input scope.

### 4.2 Exact-action approval binding

An approval is not a general permission slip. Bind it to a canonical, immutable representation of the exact proposed action. At minimum, bind:

- action type/tool name;
- normalized target/claim/resource identifier;
- amount and currency, where relevant;
- all security-relevant parameters;
- requesting user and originating task;
- policy version or policy snapshot identifier;
- approval request identifier, creation time, expiry, and single-use state.

Create a deterministic canonical serialization and cryptographic digest for the proposed action. On approval and again immediately before execution, recompute and compare the digest. Any change to amount, target, action type, or parameters invalidates the old approval and requires fresh governance evaluation. Consume approvals atomically so concurrent requests cannot use one approval twice. An agent cannot approve its own action. An approval must come from a separately authenticated user with the required manager/admin permission.

### 4.3 Policy and risk behavior

- Store policies in MongoDB and support enabled/disabled state, versioning, rule parameters, effective dates if useful, and audit history.
- Do not use Python `eval`, `exec`, arbitrary code, or LLM-generated code to evaluate policy rules. Use an explicit, validated rule schema/DSL and deterministic evaluator.
- Define conflict precedence: mandatory deny/security rules override approval; explicit deny overrides allow; approval-required rules cannot be bypassed by a low risk score; unknown/unavailable policy evaluation fails closed.
- Keep risk scoring transparent and configurable. Store score, level, factors, reasons, and recommended action. Risk scoring supplements policy; it never overrides hard policy requirements.
- Seed illustrative demo policies only, clearly marked as sample organization policy. Include the example threshold of claims above ₹5,000 requiring manager approval only as a configurable seed rule, not a universal truth.

### 4.4 Prompt injection and untrusted data

- Treat receipt text, PDFs, OCR output, user messages, external documents, model output, and tool results as untrusted data.
- A receipt can provide evidence fields (merchant, date, amount, category); it cannot issue instructions, modify policy, request secrets, or change tool permissions.
- Separate data extraction from instruction following. Use schemas and validate all extracted values deterministically.
- Prompt-injection detection is defense-in-depth, not a guarantee. The actual control is that untrusted text never receives authority and cannot bypass deterministic authorization.
- Use bounded tool allowlists, structured inputs/outputs, size limits, content-type validation, path-safe storage names, and no arbitrary file execution.

### 4.5 MongoDB correctness

- Use MongoDB Atlas + PyMongo. Create all required collections: `users`, `roles`, `expense_claims`, `receipts`, `policies`, `agent_tasks`, `tool_executions`, `approvals`, `audit_logs`, `evaluations`.
- Define schemas/document examples, required fields, indexes, references, retention expectations, and validation rules.
- Add unique indexes for normalized idempotency keys and duplicate submission fingerprints where appropriate.
- Use atomic conditional updates for approval consumption, status transitions, and idempotency. Use transactions for multi-document operations when the deployment supports them.
- MongoDB transactions require a replica set or sharded deployment. Use Atlas (or a local replica-set test setup) for transaction integration tests. Do not claim that transaction tests passed against a standalone MongoDB server or a mock that does not implement transactions.
- Design safe recovery for partial failure. If a transaction cannot be used for a workflow, explicitly document the saga/compensation strategy and intermediate states.
- Application-level append-only audit writes are not the same as cryptographic immutability. Restrict audit modification permissions and document residual risk. Do not claim tamper-proof audit logs without a separately implemented and tested control.

### 4.6 Durable LangGraph workflow

- Use a shared typed state and explicit graph nodes/edges.
- Implement persistence-backed checkpointing so paused workflows can resume after a backend restart. In-memory-only checkpoints are not sufficient for the approval/resume requirement.
- Verify the currently supported LangGraph checkpoint integration and its compatibility with the selected MongoDB/Python versions. If a MongoDB checkpoint package is unsuitable, implement a clearly tested persistence adapter rather than pretending default in-memory state is durable.
- Approval pause/resume must preserve task identity, proposed action digest, state version, and checkpoint reference. Re-run governance before continuing to execution.
- Handle duplicate resume requests, expired approvals, changed actions, rejected approvals, cancelled tasks, and interrupted workers idempotently.

### 4.7 API, auth, and real-time updates

- Version APIs under `/api/v1` and use Pydantic request/response schemas.
- Implement authentication, password hashing with Argon2 or another maintained secure choice, short-lived access tokens, refresh-token rotation/revocation, logout semantics, and server-side RBAC.
- Enforce resource ownership (users must not read another employee's claims/tasks/receipts unless their manager/admin permissions authorize it).
- Authenticate WebSocket connections and authorize access to the specific task before streaming. Never broadcast one user's task data to another user.
- Use structured errors and correct HTTP status codes. Apply rate limiting and restrictive CORS configuration.
- Store no secrets in frontend `VITE_*` variables. Anything bundled into a browser is public.

## 5. Scope and requirements to implement

Use the complete baseline specification as the detailed feature list. In particular, preserve all of these:

1. Planner, Receipt, Validation, and Execution agents coordinated with LangGraph.
2. Independent policy engine, RBAC/permissions, risk engine, governance gateway, and approval manager.
3. Simulated expense claim workflow including receipt extraction/validation, duplicate detection, risk evaluation, approval pause/resume, revalidation, execution, and audit trail.
4. The ten MongoDB collections and their indexes/schema documentation.
5. Versioned REST APIs for auth, agents/tasks, claims, governance, approvals, policies, audit, evaluations, and dashboard.
6. Authenticated task-scoped WebSocket events.
7. Frontend pages: login, registration, dashboard, agent chat, claims, claim details, approvals, policy management, audit logs, evaluation dashboard, profile, admin management.
8. Real backend-derived dashboard metrics—never hardcoded KPI numbers.
9. Security, failure handling, idempotency, retries/timeouts, recovery, and prompt-injection defenses.
10. At least 50 reproducible benchmark cases in the requested distribution, with actual measured results and a clear report.
11. Docker and deployment instructions, professional README, technical docs, Mermaid diagrams, and a three-minute demo script.

Keep the application demonstrable without mandatory paid services. Build interfaces/adapters so automated tests can use deterministic fake LLM/model and storage providers. The live Gemini provider must be real when a key is configured; a fake provider must be clearly named and used only for local/demo/test mode, never presented as live AI execution.

## 6. Resolve specification gaps explicitly

The baseline is comprehensive in breadth but some implementation-level details are not fully specified. Create entries in `DECISION_LOG.md` for at least the following and choose safe defaults unless a true blocker exists:

1. **Organization/tenant scope:** implement a single-organization MVP with an `organization_id`/tenant-ready field where practical; do not claim full multi-tenant isolation until implemented and tested.
2. **Claim lifecycle:** define draft → processing → pending approval (where needed) → approved/authorized → submitted/processed → rejected/failed/cancelled. Separate a draft claim from a sensitive submit/execute operation.
3. **Threshold boundary:** define whether “above ₹5,000” means `> 5000` (not `>= 5000`) and test boundary values ₹4,999, ₹5,000, and ₹5,001.
4. **Receipt extraction:** make extraction pluggable. Provide a deterministic fixture/test adapter and a real Gemini multimodal adapter or another chosen OCR adapter. Clearly document whether local OCR is optional and what file types are supported.
5. **File storage:** local non-public storage for development; configurable S3-compatible/cloud adapter for deployment if required. Save metadata/references in MongoDB, not large blobs in ordinary claim documents.
6. **Checkpoint persistence:** select and test an actual durable LangGraph checkpoint solution.
7. **Mongo transaction strategy:** document Atlas/replica-set requirements and fallback behavior for local unit tests.
8. **JWT refresh/logout:** decide token storage, rotation, revocation, expiry, and cookie/header approach; use secure production cookie settings if cookies are selected.
9. **Policy versioning:** specify how active policy updates affect an already pending approval; safest default is to bind approval to a policy version and re-evaluate against current mandatory restrictions before execution.
10. **Evaluation metrics:** define denominators and what counts as TP/FP/TN/FN for allow/deny/approval decisions. Never label a metric “accuracy” without a reproducible expected-outcome dataset.
11. **Operational security:** document backup, log redaction, secret rotation, retention, rate limits, and deployment hardening. Mark items requiring external infrastructure/security review as pending, not complete.
12. **Provider outages:** define timeout, retry, circuit-breaker/backoff behavior, and safe manual/fallback path. Never retry a non-idempotent sensitive operation blindly.

## 7. Required repository continuity system

Create and maintain these files in the repository:

```text
AgentShield-AI/
├── docs/
│   ├── PROJECT_REQUIREMENTS_BASELINE.md
│   ├── architecture.md
│   ├── database-design.md
│   ├── api-documentation.md
│   ├── workflow.md
│   ├── security-design.md
│   ├── testing-report.md
│   ├── deployment-guide.md
│   └── agent-handoff/
│       ├── AGENT_HANDOFF.md
│       ├── PROJECT_STATUS.md
│       ├── PHASE_TRACKER.md
│       ├── REQUIREMENT_TRACEABILITY.md
│       ├── SESSION_LOG.md
│       ├── DECISION_LOG.md
│       ├── RISK_AND_BLOCKER_LOG.md
│       └── NEXT_SESSION_PROMPT.md
├── frontend/
├── backend/
├── tests/ (or backend/tests and frontend tests, consistently documented)
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

Use the templates in this pack as the starting format. If equivalent files already exist, preserve and improve them rather than creating duplicates.

### Every agent session MUST update

- `PROJECT_STATUS.md`: current phase/subphase, overall progress, verified features, unverified features, blockers, and exact next action.
- `PHASE_TRACKER.md`: every requirement/phase item with one status and evidence.
- `REQUIREMENT_TRACEABILITY.md`: link each original requirement to implementation file(s), test(s), and proof.
- `SESSION_LOG.md`: date/time, agent/session summary, files changed, commands run, test outcomes, failures, decisions, Git commit hash if created, unfinished work.
- `DECISION_LOG.md`: every material assumption or architecture decision, rationale, consequences, and date.
- `RISK_AND_BLOCKER_LOG.md`: unresolved technical/security/deployment risks, severity, mitigation, owner/action.
- `AGENT_HANDOFF.md`: current canonical state and exact next steps for any agent.
- `NEXT_SESSION_PROMPT.md`: a complete, copy-paste prompt for the next session. It must name the exact phase, files to read, commands to run, intended files to change, acceptance criteria, tests, and stop condition.

Update these files before ending a session, especially when context is running low. A future agent must be able to continue without reading chat history.

## 8. Status vocabulary and definition of done

Use only these status values consistently:

- `NOT_STARTED` — no implementation exists.
- `IN_PROGRESS` — implementation is actively being developed.
- `IMPLEMENTED_UNTESTED` — code exists but required tests/acceptance checks have not passed.
- `VERIFIED` — implementation meets documented acceptance criteria and relevant tests passed in the recorded environment.
- `PARTIAL` — some required behavior is implemented, but scope is incomplete.
- `BLOCKED` — progress requires a missing external dependency, unresolved decision, or failing prerequisite.
- `DEFERRED` — explicitly moved out of current delivery scope with reason and owner visibility.
- `NOT_APPLICABLE` — requirement demonstrably does not apply; include reason.

A feature may be `VERIFIED` only when:

1. Code is present and integrated.
2. Acceptance criteria are written and met.
3. Relevant automated tests pass.
4. Required manual/integration verification is recorded when automation cannot cover it.
5. Security and authorization paths have tests for sensitive functionality.
6. Documentation and traceability are updated.

A test that was not run is not a passing test. A skipped test is not a passing test. A mock test does not prove a live external integration. Never invent test output, benchmark scores, screenshots, API responses, deployment status, or security claims.

## 9. Original 12-phase delivery plan and exit gates

Keep this phase order unless a dependency requires a documented reorder. Split a phase into subphases if it is too large for one session; never silently skip its requirements.

### Phase 1 — Requirements and Project Planning
- Inspect repository and available tools/versions.
- Build requirement traceability matrix.
- Record ambiguities and decisions.
- Define modular architecture, trust boundaries, data flow, state machines, and security threat model.
- Define MongoDB collections/indexes and API contracts.
- Create Mermaid diagrams that match the planned system.
- Create phased backlog, acceptance criteria, environment checklist, and initial handoff files.
- Exit gate: planning documents are internally consistent, scope and assumptions are recorded, and Phase 2 tasks are explicit. Do not build the whole application here.

### Phase 2 — Project Initialization
- Create/reconcile frontend and backend structures.
- Establish dependency files and lockfiles.
- Create configuration and `.env.example`.
- Create minimal health endpoints/pages.
- Verify frontend and backend start commands.
- Exit gate: clean local startup documented; no real credentials committed.

### Phase 3 — Database and Authentication
- Implement MongoDB connection lifecycle, collection access, indexes, validation, and seed data.
- Implement password hashing, JWT access/refresh flow, logout/revocation, roles, permissions, resource ownership.
- Test user and role boundaries, invalid/expired/revoked tokens, and database failures.
- Exit gate: auth and RBAC tests pass against isolated test data.

### Phase 4 — Governance Engine
- Implement typed action proposals, policy versioning/evaluation, RBAC permission manager, risk scoring, gateway, append-only audit writer, and governance decision schema.
- Test ALLOW, DENY, REQUIRE_APPROVAL, precedence, policy unavailability, unauthorized identities, and fail-closed behavior.
- Exit gate: privileged executor is inaccessible except through gateway; governance tests pass.

### Phase 5 — Controlled Tools
- Implement receipt storage/extraction interface, schema validation, expense validation, duplicate checker, and claim executor.
- Add idempotency, unique indexes, status transitions, safe retries, and failure handling.
- Ensure tools accept only validated structured data and are callable only through authorization boundary.
- Exit gate: controlled-tool tests cover duplicates, invalid inputs, retries, and denied actions.

### Phase 6 — Multi-Agent System
- Implement Planner, Receipt, Validation, and Execution agents and shared LangGraph state.
- Integrate Gemini through a provider interface, structured outputs, timeouts, and bounded tool routing.
- Add persistent checkpointing and deterministic fake provider for tests.
- Exit gate: agent graph can prepare a task but cannot execute a privileged action without gateway authorization; workflow tests pass.

### Phase 7 — Human Approval
- Implement approval creation, manager authorization, approve/reject, expiry, immutable action digest, single-use consumption, graph pause, durable resume, and post-approval revalidation.
- Test changed action, expired approval, self-approval attempt, duplicate approval request, concurrent consumption, rejection, process restart, and resume retry.
- Exit gate: persisted approval/resume works across backend restart using real persistence integration tests.

### Phase 8 — Frontend
- Build authentication, dashboard, chat, claims, claim detail, approvals, policies, audit, evaluations, profile, and admin pages.
- Use accessible and responsive components and real API state.
- Use actual backend data; display empty/loading/error states; do not fabricate KPI values.
- Exit gate: role-specific pages and actions are connected to real APIs and access control is enforced server-side.

### Phase 9 — Integration
- Connect REST APIs and authenticated WebSockets.
- Implement task lifecycle display and governance/approval progress.
- Verify complete expense workflow with seeded synthetic data.
- Exit gate: end-to-end happy path, deny path, and approval/resume path work end to end.

### Phase 10 — Testing and Evaluation
- Implement at least 50 benchmark cases using the exact distribution in baseline: 15 valid; 10 approval-required; 8 unauthorized access; 7 duplicate/invalid receipt; 5 prompt-injection/tool-abuse; 5 service-failure/recovery.
- Compute metrics from an explicit expected-outcome dataset and actual run records.
- Run backend, frontend, integration, authorization, failure, and regression suites.
- Generate reproducible report with command, environment, timestamp, totals, failed cases, metric definitions, and limitations.
- Exit gate: results are real and reproducible; no critical test is silently skipped.

### Phase 11 — Deployment
- Add Dockerfiles/Compose and production configuration.
- Configure secrets, CORS, HTTPS termination, health checks, storage, logs, database access, backup/restore guidance, and deployment steps.
- Deploy only when the owner supplies required credentials and confirms the target service.
- Exit gate: deployed environment smoke tests pass, or deployment is marked BLOCKED with exact missing requirements.

### Phase 12 — Final Preparation
- Finish README/docs/diagrams and update them to match implementation.
- Prepare screenshots only from the real application.
- Prepare three-minute demo flow, presentation outline, limitations, and reproducibility guide.
- Run final acceptance checklist.
- Exit gate: project status reports only evidence-backed VERIFIED/PARTIAL/BLOCKED/DEFERRED states.

## 10. Required development workflow in every session

At the start:

1. Run `git status --short --branch`; do not discard uncommitted work.
2. Read `AGENT_HANDOFF.md`, `PROJECT_STATUS.md`, `PHASE_TRACKER.md`, `NEXT_SESSION_PROMPT.md`, and relevant decision/risk entries.
3. Inspect the actual files named by the handoff.
4. Verify the last recorded test state with targeted commands; do not assume it remains valid.
5. Identify one bounded goal for this session. If a phase is too large, choose one coherent subphase and write its acceptance criteria.

While working:

1. Implement real behavior, not placeholders disguised as working features.
2. Prefer small, reviewable changes and preserve the current folder structure unless there is a strong reason to change it.
3. Add or update tests with each implementation slice.
4. Avoid unrelated refactors and unnecessary dependencies.
5. Never automatically overwrite `.env`, user data, uploads, or uncommitted source files.
6. Do not install a package until checking whether it is already present and whether the selected version is compatible.
7. If an external credential is absent, implement/test a safe adapter or mark the live integration `BLOCKED`; do not fabricate success.
8. Run targeted tests after each slice, then broader tests before marking it verified.

At the end:

1. Run formatting/lint/type checks that exist and all relevant tests.
2. Record exact commands, exit codes, counts, and any skipped tests.
3. Inspect `git diff` and `git status` for accidental files, secrets, generated artifacts, or unrelated changes.
4. Update all continuity files listed in Section 7.
5. Write `NEXT_SESSION_PROMPT.md` as a complete prompt usable by a different agent.
6. Create a local Git commit for a coherent, verified milestone when appropriate and safe. Never force-push, rewrite history, or push to a remote without explicit authorization.
7. Do not start the next major phase in the same session after completing the bounded scope unless doing so is necessary to finish the agreed small slice. Stop at the documented handoff boundary.

## 11. Initial-session instructions — what to do now

You are starting the initial build/planning session. Do this now:

1. Inspect the repository and determine whether it is empty, partially built, or already contains working code.
2. Read the entire requirements baseline.
3. Check available local versions for Python, Node/npm, Git, Docker, and any existing MongoDB connection setup. Do not install or upgrade anything yet.
4. Create/reconcile the `docs/` and `docs/agent-handoff/` files listed above using the supplied templates where useful.
5. Produce Phase 1 planning artifacts: architecture, trust-boundary design, workflow/state machine, DB design, API contract, Mermaid diagrams, risk register, environment inventory, and requirements traceability.
6. Record all assumptions and unresolved questions. Use the safe default rules in Section 6 for non-blocking details.
7. Build a detailed, ordered Phase 2 backlog with file paths, acceptance criteria, test commands, and prerequisites.
8. Update `README.md` with current project status and how to proceed, but do not pretend the application already exists.
9. Update every handoff/status file and generate `NEXT_SESSION_PROMPT.md` for Phase 2.
10. Report a concise session summary: repository condition, decisions made, documents created/updated, tests or checks actually run, blockers, and the exact next step.

**Stop after Phase 1 planning and the handoff are complete. Do not attempt all 12 phases in this first session.**

## 12. Final quality standard

A successful project is not a visually convincing dashboard alone. It must demonstrate, with code and tests, that:

- multiple agents can prepare and coordinate a multi-step task;
- agents cannot bypass the deterministic governance gateway;
- a prohibited action is denied;
- a sensitive action is paused for an authorized manager;
- approval is tied to the exact action and cannot be replayed or mutated;
- the workflow resumes after approval, including after restart;
- every important decision and tool execution is auditable;
- dashboards and benchmark reports use actual data;
- failures default safely and recovery is tested.

Never say “fully secure”, “100% accurate”, or “production-ready” without clearly defined evidence and independent review. Be precise about limitations.
