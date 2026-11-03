# Decision Log — AgentShield AI

| # | Date | Decision | Rationale | Consequences |
|---|------|----------|-----------|--------------|
| D001 | 2026-11-03 | Amount threshold: `> 5000` (not `>= 5000`) triggers REQUIRE_APPROVAL | Spec says "above ₹5,000" which means strictly greater than. ₹5,000 itself is ALLOW. | Test boundary values 4999, 5000, 5001 |
| D002 | 2026-11-03 | Single-organization MVP, no multi-tenant isolation | Hackathon scope; add tenant_id field for future | No tenant isolation in auth/queries |
| D003 | 2026-11-03 | MemorySaver for LangGraph checkpointing in MVP | langgraph-checkpoint-mongodb available but MemorySaver simpler for demo | Workflows don't survive backend restart; document as limitation |
| D004 | 2026-11-03 | bcrypt for password hashing (already installed) | argon2 not installed; bcrypt 5.0.0 is available and secure | No change needed |
| D005 | 2026-11-03 | PyJWT for JWT tokens | Standard, lightweight | Need to install if not present |
| D006 | 2026-11-03 | Local file storage for MVP, adapter pattern for S3 | No S3 credentials needed for demo | storage/ directory, gitignored |
| D007 | 2026-11-03 | Mock LLM as default, Gemini when API key configured | Free testing, no API costs during dev | LLM_PROVIDER=mock in .env |
| D008 | 2026-11-03 | Approval binding: SHA-256 of canonical action (tool, amount, category, employee, receipt_id) | Notes excluded from hash (non-execution field) | Amount/category/target changes invalidate approval |
| D009 | 2026-11-03 | Policy versioning: increment version on update, bind approval to policy version | Re-evaluate against current mandatory restrictions before execution | Policy changes while pending → revalidation catches |
| D010 | 2026-11-03 | Header-based role for API demo, JWT for production paths | Faster demo; auth middleware handles both | X-Role header in dev mode only |
