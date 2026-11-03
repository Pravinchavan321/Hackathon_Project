# AgentShield AI

> **Autonomous Intelligence. Governed Execution. Trusted Outcomes.**
> 
> *A Policy-Governed Framework for Secure and Autonomous AI Agent Execution.*

---

## 💡 What is AgentShield AI?

AgentShield AI is an enterprise-grade platform for running autonomous multi-agent systems with an **independent, deterministic governance layer**.

In modern AI architectures, when an LLM decides to call a tool, it executes directly. AgentShield AI introduces a strict trust boundary:
> **"AI agents can decide HOW to accomplish a task, but they cannot decide whether they are AUTHORIZED to perform a sensitive action. That authority belongs to the independent governance engine."**

---

## 📊 Live Evaluation Results (Locked 50-Task Benchmark)

| Evaluation Metric | Baseline Agent (No Governance) | AgentShield AI (Governed) | Hackathon Target | Status |
|:---|:---:|:---:|:---:|:---:|
| **Task Success Rate** | 100.0% | **100.0%** | $\ge 85\%$ | **PASSED** |
| **Policy Violation Rate** | 100.0% *(All Bypassed)* | **0.0%** *(Zero Bypassed)* | **0.0%** | **PASSED** |
| **Approval Trigger Rate** | 0.0% *(Ran Unchecked)* | **100.0%** *(All Paused)* | **100.0%** | **PASSED** |
| **Prompt Injection Block Rate** | 0.0% *(Attacks Succeeded)* | **100.0%** *(All Neutralized)*| **100.0%** | **PASSED** |
| **Governance Decision Latency** | — | **4.37 ms** | $< 50\text{ ms}$ | **PASSED** |

*All results verified by automated test harness (`eval/run_eval.py`). Raw execution data in `results/results.json`.*

---

## 🏛️ System Architecture

```
User Prompt + Receipt
         │
         ▼
┌────────────────────────────────────────┐
│     Autonomous LangGraph Pipeline      │
│  Planner ➔ Receipt ➔ Validation ➔ Exec │
│        (Generates Proposed Action)     │
└───────────────────┬────────────────────┘
                    │
                    ▼
══════════════════════════════════════════
 🛡️ INDEPENDENT GOVERNANCE GATEWAY (CODE)
   - Evaluates RBAC & Resource Ownership
   - Deterministic Policy Engine (MongoDB)
   - Explainable Risk Engine (0-100)
   - Cryptographic Exact-Action Binding
   - Atomic Human Approval Workflow
══════════════════════════════════════════
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
     [ ALLOW ]  [ DENY ]  [ REQUIRE_APPROVAL ]
         │          │          │
         ▼          ▼          ▼
    Controlled    Blocked    Workflow Pauses
    Tool Exec     + Audit    for Human Sign-off
```

---

## 🚀 Quickstart (Run in 4 Commands)

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Run Test Suite (14 Verification Tests)
```bash
pytest tests/ -v
```

### 3. Run 50-Task Benchmark Evaluation
```bash
python -m eval.run_eval
```

### 4. Launch Live Demo Dashboard
```bash
uvicorn app.api:app --reload
```
Open **`http://localhost:8000`** in your browser.

---

## 📂 Repository Documentation Guide

Complete architectural and operational specifications:

| Document | Description |
|:---|:---|
| [`docs/METRICS.md`](docs/METRICS.md) | **Locked Benchmark Metrics**, formula definitions, targets, and test set |
| [`docs/problem-statement.md`](docs/problem-statement.md) | Core enterprise problem statement & threat analysis |
| [`docs/objectives.md`](docs/objectives.md) | Five measurable project objectives |
| [`docs/architecture.md`](docs/architecture.md) | High-level system architecture, trust boundary, and component diagrams |
| [`docs/database-design.md`](docs/database-design.md) | MongoDB 10 collection schemas, indexes, and document examples |
| [`docs/api-documentation.md`](docs/api-documentation.md) | Full v1 REST API & WebSocket event specifications |
| [`docs/workflow.md`](docs/workflow.md) | End-to-end multi-agent orchestration lifecycle & state machines |
| [`docs/security-design.md`](docs/security-design.md) | STRIDE threat model, prompt injection defense, and cryptographic action binding |
| [`docs/testing-report.md`](docs/testing-report.md) | Benchmark methodology, empirical test outputs, and safety analysis |
| [`docs/deployment-guide.md`](docs/deployment-guide.md) | Step-by-step local setup, environment variables, and Docker Compose guide |
| [`docs/demo-script.md`](docs/demo-script.md) | 3-minute hackathon presentation script & judge demonstration flow |
| [`docs/agent-handoff/`](docs/agent-handoff/) | Decision logs, project status, RTM, and session handoffs |

---

## 🔒 Security Assertions & Limitations
- **Security is in Code:** Governance decisions are executed in deterministic Python modules, never via stochastic LLM prompting.
- **Fail-Closed:** Missing parameters, rule ambiguities, or database timeouts immediately yield a `DENY` decision.
- **Simulated Business Process:** The demonstration workflow simulates an expense reimbursement process with synthetic data; no actual financial transfers occur.
