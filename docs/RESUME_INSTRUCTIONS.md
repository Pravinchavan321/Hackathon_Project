# How to Resume Development — AgentShield AI Guide

Agar session ki context window ya token limit hit ho jaye, ya tum kisi nayi chat/agent me project continue karna chahte ho, toh ye simple guide follow karo.

---

## 1. Kaunsi File Me Sare Phases Hain?

Sare **12 Phases**, unke deliverables, entry/exit criteria aur live status is file me hain:
👉 **[`docs/agent-handoff/PHASE_TRACKER.md`](docs/agent-handoff/PHASE_TRACKER.md)**

Iske alawa summary aur architecture in files me hai:
- **Metrics & Targets:** [`docs/METRICS.md`](docs/METRICS.md)
- **Live Project Status:** [`docs/agent-handoff/PROJECT_STATUS.md`](docs/agent-handoff/PROJECT_STATUS.md)
- **Architecture & Flow:** [`docs/architecture.md`](docs/architecture.md)

---

## 2. Limit Hit Hone Par Kaam Kaise Resume Hoga?

Tumhe purani chat history ki bilkul zaroorat nahi padegi! Hamne repository ke andar **Autonomous Continuity System** bana diya hai:

1. **Sari Progress Saved Hai:** Jitne bhi architectural decisions, 50-task benchmark tests, policies, aur code hain, wo sab disk par commit aur saved hain.
2. **Current State Logged Hai:** [`docs/agent-handoff/AGENT_HANDOFF.md`](docs/agent-handoff/AGENT_HANDOFF.md) me likha hai ki last session me kya complete hua aur agla exact step kya hai.
3. **Tests Verify Karate Hain:** Naya agent aate hi `pytest tests/` aur `python -m eval.run_eval` chala kar verify karega ki pichhla kaam intact hai.

---

## 3. Nayi Chat / Agent Me EXACT Prompt Kya Dena Hai?

Jab bhi limit hit ho ya naya session shuru ho, tum bas **niche diya gaya prompt copy-paste kar dena**:

```markdown
Resume the development of AgentShield AI from the saved repository state.

Mandatory reading order:
1. Read `docs/agent-handoff/AGENT_HANDOFF.md` completely.
2. Read `docs/agent-handoff/PROJECT_STATUS.md` and `docs/agent-handoff/PHASE_TRACKER.md`.
3. Check `docs/agent-handoff/NEXT_SESSION_PROMPT.md` for the current bounded goal.
4. Verify current test and benchmark health by running:
   - `pytest tests/ -v`
   - `python -m eval.run_eval`

Implementation & Continuous Tracking Rules:
- Continue the active phase following the instructions in `docs/agent-handoff/NEXT_SESSION_PROMPT.md`.
- Work in small verifiable steps, and do not overwrite working code.
- Test every implementation change with real test execution before claiming completion.
- CRITICAL (Continuous Update Rule): Jaise-jaise koi sub-task ya phase complete hota jaye, session end hone se pehle repository ki continuity files ko zaroor UPDATE karna:
  1. `docs/agent-handoff/PHASE_TRACKER.md` (Update status to VERIFIED with exact test evidence).
  2. `docs/agent-handoff/PROJECT_STATUS.md` (Update overall progress %, verified features, and current blocker state).
  3. `docs/agent-handoff/SESSION_LOG.md` (Record exact files changed, commands run, test counts, and exit codes).
  4. `docs/agent-handoff/NEXT_SESSION_PROMPT.md` (Write the fresh copy-paste prompt for the subsequent turn).
```

Ye instruction dene se agent naya phase complete karte hi **tracking files ko automatically update kar dega**, taaki tumhara progress record hamesha 100% accurate rahe!
