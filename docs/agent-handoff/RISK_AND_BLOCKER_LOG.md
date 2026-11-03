# Risk and Blocker Log — AgentShield AI

| Risk ID | Category | Description | Severity | Probability | Mitigation Strategy | Owner | Status |
|:---|:---|:---|:---:|:---:|:---|:---:|:---:|
| **RSK-001** | LLM API | Gemini API rate limits, network latency, or quota exhaustion during hackathon judging. | HIGH | MEDIUM | Implement a deterministic `MockLLMProvider` fallback for all automated evaluations and live demo runs; toggled instantly via `LLM_PROVIDER=mock`. | Backend | `MITIGATED` |
| **RSK-002** | Database | MongoDB Atlas network connectivity issues during remote evaluation. | MEDIUM | LOW | Provide full in-memory fallback state machine (`app/tools.py::Env`) and local Docker MongoDB container configuration in `docker-compose.yml`. | Database | `MITIGATED` |
| **RSK-003** | Security | Prompt injection modifying parsed invoice values before the execution node. | HIGH | HIGH | Structured Pydantic validation on all extracted fields; Governance Gateway enforces strict policy checks on raw extracted numbers regardless of prompt notes. | Security | `MITIGATED` |
| **RSK-004** | Concurrency | Race condition where a manager double-clicks "Approve", executing duplicate claim side-effects. | HIGH | MEDIUM | Enforce atomic single-use approval consumption in database using conditional queries (`status == PENDING`) and unique idempotency keys on executions. | Backend | `MITIGATED` |
| **RSK-005** | Statefulness | Checkpointed LangGraph state lost if server restarts during a pending approval. | MEDIUM | LOW | Abstract checkpointing behind `MemorySaver` for hackathon MVP; state persistence documented in MongoDB repository schema for production. | Architecture | `DOCUMENTED` |
| **RSK-006** | Scope Creep | Attempting to build production financial banking integrations rather than simulated approval governance. | HIGH | HIGH | Explicitly restrict scope to simulated enterprise reimbursement workflows with synthetic test identities. | Lead | `MITIGATED` |
