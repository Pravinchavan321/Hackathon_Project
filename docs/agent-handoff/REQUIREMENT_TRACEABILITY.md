# Requirement Traceability Matrix (RTM) — AgentShield AI

| Req ID | Baseline Requirement Summary | Target Architecture Module | Primary Implementation File(s) | Verification Test File(s) | Status |
|:---|:---|:---|:---|:---|:---:|
| **REQ-01** | Multi-agent coordination with LangGraph | Orchestration Layer | `app/orchestration/graph.py`, `app/orchestration/nodes.py` | `tests/test_governance.py` | `IMPLEMENTED_UNTESTED` |
| **REQ-02** | 4 Specialized Agents (Planner, Receipt, Validation, Execution) | Agent Layer | `app/agents/planner_agent.py`, `receipt_agent.py`, `validation_agent.py`, `execution_agent.py` | `tests/test_governance.py` | `IMPLEMENTED_UNTESTED` |
| **REQ-03** | Independent Deterministic Governance Engine | Governance Layer | `app/governance/policy_engine.py`, `governance_gateway.py` | `tests/test_governance.py` | `VERIFIED` |
| **REQ-04** | Role-Based Access Control (EMPLOYEE, MANAGER, ADMIN) | Identity / RBAC | `app/governance/permission_manager.py`, `app/middleware/auth_middleware.py` | `tests/test_governance.py`, `tests/test_api.py` | `VERIFIED` |
| **REQ-05** | Explainable Risk Assessment Scoring (0–100, Tiered) | Governance Layer | `app/governance/risk_engine.py` | `tests/test_governance.py` | `VERIFIED` |
| **REQ-06** | Human Approval with Exact-Action Cryptographic Hash | Governance Layer | `app/governance/approval_manager.py` | `tests/test_governance.py` | `VERIFIED` |
| **REQ-07** | Single-Use Atomic Approval Consumption | Persistence Layer | `app/governance/approval_manager.py` | `tests/test_governance.py`, `tests/test_api.py` | `VERIFIED` |
| **REQ-08** | Workflow Pause (interrupt) and Resume (Command) | Orchestration Layer | `app/orchestration/graph.py`, `app/agents.py` | `tests/test_governance.py` | `VERIFIED` |
| **REQ-09** | Revalidation of Policy & Permissions on Resume | Governance Layer | `app/governance/governance_gateway.py`, `app/orchestration/nodes.py` | `tests/test_governance.py` | `VERIFIED` |
| **REQ-10** | Simulated Expense Claim Tool (No real financial transfer) | Controlled Tools | `app/tools/claim_executor.py`, `app/tools.py` | `tests/test_governance.py` | `VERIFIED` |
| **REQ-11** | Receipt Data Extraction & Ingestion Security | Controlled Tools | `app/tools/receipt_reader.py`, `app/agents/receipt_agent.py` | `tests/test_governance.py` | `VERIFIED` |
| **REQ-12** | Duplicate Claim Detection (Receipt hash & fingerprint) | Controlled Tools | `app/tools/duplicate_checker.py` | `tests/test_governance.py` | `VERIFIED` |
| **REQ-13** | MongoDB 10 Collections Design & Indexes | Database Layer | `app/database/collections.py`, `app/database/indexes.py` | `tests/test_governance.py` | `VERIFIED` |
| **REQ-14** | REST API v1 Endpoints (Auth, Claims, Tasks, Approvals) | API Layer | `app/api/*.py`, `app/api.py` | `tests/test_api.py` | `VERIFIED` |
| **REQ-15** | Real-time WebSocket Task Events | API Layer | `app/api/websocket_routes.py`, `app/api.py` | `tests/test_api.py` | `IMPLEMENTED_UNTESTED` |
| **REQ-16** | Frontend 12-Page Dashboard (React + Tailwind) | Frontend Layer | `frontend/src/pages/*.jsx`, `dashboard/index.html` | Manual E2E checks | `IN_PROGRESS` |
| **REQ-17** | Real Backend-Derived Dashboard Metrics (No mocked KPIs) | Dashboard / API | `app/api/dashboard_routes.py`, `eval/run_eval.py` | `eval/run_eval.py` | `VERIFIED` |
| **REQ-18** | Prompt Injection Defense & Untrusted Data Fencing | Security Layer | `app/governance/governance_gateway.py` | `tests/test_governance.py`, `eval/run_eval.py` | `VERIFIED` |
| **REQ-19** | 50-Task Reproducible Benchmark Suite | Evaluation Layer | `data/generate_tasks.py`, `eval/run_eval.py` | `eval/run_eval.py` | `VERIFIED` |
| **REQ-20** | Docker & Deployment Configurations | DevOps Layer | `docker-compose.yml`, `docs/deployment-guide.md` | Deployment checks | `VERIFIED` |
