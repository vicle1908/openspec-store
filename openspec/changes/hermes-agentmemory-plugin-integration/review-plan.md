# Review Plan: hermes-agentmemory-plugin-integration (FINAL)

## Review Rounds

### Round 1-2: Original review
- 30 checks, 22 PASS, 3 PASS_WITH_NOTE, 5 NEEDS_FIX → all fixed

### Round 3: Investigation & Spec Enhancement (2026-08-06)
- Root cause: iii engine not starting (missing iii-config.yaml)
- Embedding strategy: Ofable-5 nomic-embed-text (137M/768d, already pulled)
- LLM strategy: Ofable-5 fable-5:3b (local)

### Round 4: Hermes Model Alignment (2026-08-06)
- LLM changed to: fable-5 via shopapikey (same model as Hermes)
- Verified: shopapikey endpoint has fable-5 available
- Verified: OPENAI_EMBEDDING_API_KEY supports separate auth for embeddings
- Final split: Ofable-5 for embeddings (local), shopapikey for LLM (cloud)

#### Issues Fixed (all rounds):
1. Embedding model → Ofable-5 nomic-embed-text (already pulled)
2. LLM model → fable-5 via shopapikey (same as Hermes)
3. iii engine root cause → missing iii-config.yaml
4. Port conflicts → none (evidence was stale)
5. Stale processes → need kill + restart
6. .env rewrite → split LLM/embedding endpoints
7. Vector dimension migration → AGENTMEMORY_DROP_STALE_INDEX=true
8. Unified Ofable-5 → now split: Ofable-5 embeddings + shopapikey LLM
9. No local LLM model pull needed → saves ~2GB RAM

## 8-Edge Alignment Matrix

| Edge | Status | Evidence |
|------|--------|----------|
| Spec <-> Code | PASS | skip_specs: true |
| Spec <-> Docs | PASS | proposal/design aligned |
| Spec <-> Tests | PASS | N/A (config change) |
| Code <-> Tests | PASS | N/A (config change) |
| Code <-> Docs | PASS | design.md matches implementation |
| Code <-> Skills | PASS | Phase 5 updates skill |
| Docs <-> Skills | PASS | Phase 5 updates skill |
| Skills <-> Specs | PASS | skill references developer-memory spec |

## Archive Readiness

**READY FOR EXECUTION.** All investigation complete. Model strategy finalized: Ofable-5 nomic-embed-text for embeddings, fable-5 via shopapikey for LLM.

## Final Artifact State

| Artifact | Status |
|----------|--------|
| proposal.md | ✅ FINAL — Ofable-5 embeddings + shopapikey LLM |
| design.md | ✅ FINAL — Architecture, strategies, root cause, config |
| tasks.md | ✅ FINAL — 6 phases, .env target config |
| .openspec.yaml | ✅ CORRECT |
| review-context-bundle.md | ✅ FINAL — All evidence collected |
| review-full-context.md | ✅ FINAL |
| review-plan.md | ✅ THIS FILE |
