# Review Plan: hermes-agentmemory-plugin-integration (REVISED)

## Review Rounds

### Round 1: Initial Review (original)
- 5 parallel reviewers (Tool Version, Security, Task Completeness, Architecture, Product Scope)
- 30 checks total
- Result: 22 PASS, 3 PASS_WITH_NOTE, 5 NEEDS_FIX, 0 FAIL

### Round 2: Re-review (original)
- 5 parallel reviewers re-checked all fixes
- All 5 fixes verified correct

### Round 3: Investigation & Spec Enhancement (2026-08-06)
- Deep investigation of runtime state, port conflicts, embedding models, LLM options
- Root cause identified: iii engine not starting due to missing iii-config.yaml
- Embedding strategy revised: Ofable-5 nomic-embed-text (already pulled, higher quality)
- LLM strategy revised: Ofable-5 fable-5:3b (~2GB RAM) instead of fable-5:7b (~4.7GB)
- Ports: no conflicts found (evidence bundle was stale)
- Single server constraint confirmed

#### Findings Fixed:
1. **Embedding model** (HIGH) — Changed from @xenova/transformers (all-MiniLM-L6-v2, 22M/384d) to Ofable-5 nomic-embed-text (137M/768d). Already pulled, 3.4x more params, 2x richer representation, GPU-accelerated.
2. **LLM model** (HIGH) — Changed from fable-5:7b to fable-5:3b. 3B is adequate for compression, uses 60% less RAM (2GB vs 4.7GB), leaves headroom on M1 16GB.
3. **iii engine root cause** (CRITICAL) — Identified missing iii-config.yaml as root cause of 1489+ reconnect attempts. Bundled config exists but needs to be copied to ~/.agentmemory/ with absolute paths.
4. **Port conflict** (MEDIUM) — Evidence bundle claimed port 3111 closed. Investigation shows ports 3111, 3112, 49134 are all FREE. Only 3113 is occupied (by agentmemory viewer itself).
5. **Stale processes** (HIGH) — Two stale processes running: agentmemory (degraded, 1489+ reconnects) and agentmemory-mcp (7-tool shim fallback). Both need to be killed and restarted.
6. **Ofable-5 models** (HIGH) — Ofable-5 running but only nomic-embed-text pulled. Need to pull fable-5:3b for LLM compression.
7. **Phase 0 added** (MEDIUM) — New prerequisite phase to fix engine startup before server start.
8. **Unified Ofable-5** (MEDIUM) — Single Ofable-5 instance handles both embeddings (nomic-embed-text) and LLM (fable-5:3b), minimizing resource usage.
9. **Vector dimension migration** (LOW) — Switching from 384-dim to 768-dim requires AGENTMEMORY_DROP_STALE_INDEX=true to rebuild vector index.

## 8-Edge Alignment Matrix

| Edge | Status | Evidence |
|------|--------|----------|
| Spec <-> Code | PASS | skip_specs: true, no spec delta needed |
| Spec <-> Docs | PASS | proposal Why/What Changes sections present |
| Spec <-> Tests | PASS | N/A (config change, no tests) |
| Code <-> Tests | PASS | N/A (config change, no code) |
| Code <-> Docs | PASS | design.md matches implementation approach |
| Code <-> Skills | PASS | workspace-knowledge-tools skill will be updated |
| Docs <-> Skills | PASS | Phase 5 updates skill |
| Skills <-> Specs | PASS | skill references developer-memory spec |

## Archive Readiness

**READY FOR EXECUTION.** All investigation complete. Root causes identified. Specs enhanced with corrected model choices, port analysis, and unified Ofable-5 strategy. No CRITICAL findings remaining — Phase 0 addresses all blockers.

## Final Artifact State

| Artifact | Status | Notes |
|----------|--------|-------|
| proposal.md | REVISED | Phase 0, Ofable-5 embedding/LLM strategy, corrected model refs |
| design.md | REVISED | Architecture diagram, Ofable-5 embedding analysis, LLM analysis, port investigation, iii engine root cause, unified config |
| tasks.md | REVISED | 6 phases (0-5 + archive), Ofable-5 .env config, fresh evidence block |
| .openspec.yaml | CORRECT | schema: spec-driven, skip_specs: true |
| review-context-bundle.md | REVISED | Ofable-5 embedding evidence, nomic-embed-text verification |
| review-full-context.md | REVISED | Full context bundle with Ofable-5 strategy |
| review-plan.md | THIS FILE | Updated with Round 3 findings |
