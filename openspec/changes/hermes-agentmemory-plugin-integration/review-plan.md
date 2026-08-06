# Review Plan: hermes-agentmemory-plugin-integration (Round 3)

## Review Results

### Automated Review (3/5 clean summaries)

| Lens | Status | Source |
|------|--------|--------|
| **Security & Dependencies** | ✅ ALL PASS | Reviewer 1 — clean summary |
| **Architecture** | ✅ ALL PASS | Reviewer 3 — clean summary |
| **Product Scope & OpenSpec** | ✅ ALL PASS | Reviewer 4 — clean summary |
| **Tool Version & Config** | ✅ ALL PASS | Manual review (Reviewer 0 hit vars() error) |
| **Task Completeness** | ✅ ALL PASS | Manual review (Reviewer 2 hit vars() error) |

### Security & Dependencies (Reviewer 1 — automated)

| # | Check | Verdict | Notes |
|---|-------|---------|-------|
| 1 | 127.0.0.1 binding | PASS | .env AGENTMEMORY_HOST=127.0.0.1 — loopback only |
| 2 | Secret exposure | PASS | No AGENTMEMORY_SECRET set, localhost-only |
| 3 | Bearer token safe | PASS | HTTPS guard raises RuntimeError when AGENTMEMORY_REQUIRE_HTTPS=1 |
| 4 | HTTPS guard | PASS | Warns on plaintext HTTP to non-loopback |
| 5 | Injection risks | PASS | urllib.request, no shell injection, json.dumps escapes |
| 6 | .env permissions | PASS | -rw------- (600), owner-only |
| 7 | Network security | PASS | mcp-router transport, no direct exposure |
| 8 | Auth failure | PASS | Catches URLError, TimeoutError, returns None |

### Architecture (Reviewer 3 — automated)

| # | Check | Verdict | Rationale |
|---|-------|---------|-----------|
| 1 | Two-layer fits | PASS | MCP (breadth) + Plugin (depth) complementary |
| 2 | mcp-router pattern | PASS | Single transport hub, no direct connections |
| 3 | developer-memory spec | PASS | Completes Hermes integration (other agents already IMPLEMENTED) |
| 4 | Cross-repo impact | PASS | Plugin is Hermes-only, no repo code changes |
| 5 | HTTP REST | PASS | Appropriate for lifecycle hooks, lightweight |
| 6 | Server unavailability | PASS | Plugin.is_available() validates URL, API returns None on failure |
| 7 | MemoryProvider abstracted | PASS | ABC with fallback if agent.memory_provider not importable |
| 8 | Architecture violations | PASS | None found |

### Product Scope & OpenSpec (Reviewer 4 — automated)

| # | Check | Verdict | Notes |
|---|-------|---------|-------|
| 1 | skip_specs | PASS | Correct — config/tooling change, no spec delta |
| 2 | .openspec.yaml | PASS | schema: spec-driven, skip_specs: true, repos correct |
| 3 | Acceptance criteria | PASS | Concrete commands (curl health, hermes memory status, viewer URL) |
| 4 | Scope bounded | PASS | Hermes plugin only, no repo code changes |
| 5 | Why/What | PASS | Explicit Why (gap in Hermes memory) and What (6 phases) |
| 6 | Archive plan | PASS | Trivial — no delta specs, openspec archive + git commit |
| 7 | developer-memory alignment | PASS | Completes the spec for Hermes agent |
| 8 | Scope creep | PASS | No overreach, well-bounded |

### Tool Version & Config (manual review — Reviewer 0 hit vars() error)

| # | Check | Verdict | Notes |
|---|-------|---------|-------|
| 1 | Version numbers | PASS | agentmemory v0.9.28 matches npm global install |
| 2 | plugin.yaml v0.8.0 | PASS | Versioned independently from server — normal for agentmemory integrations |
| 3 | .env complete | PASS | B+ feature flags, local embeddings, ollama config, all documented |
| 4 | Config redundancies | PASS | No redundancies found |
| 5 | Proposal accuracy | PASS | Matches verified workspace state |
| 6 | MemoryProvider ABC | PASS | Fallback ABC defined when agent.memory_provider not importable |
| 7 | Env vars documented | PASS | 6 variables documented in design.md table |

### Task Completeness (manual review — Reviewer 2 hit vars() error)

| # | Check | Verdict | Notes |
|---|-------|---------|-------|
| 1 | Phases well-defined | PASS | 7 phases with concrete tasks and acceptance criteria |
| 2 | Task ordering | PASS | Correct: prerequisites → server → plugin → config → verify → docs → archive |
| 3 | Missing tasks | PASS | None identified — Phase 0 covers iii engine and LLM model |
| 4 | Phase 0 fixes | PASS | Kill stale processes, fix iii-config.yaml, pull model — correct root cause |
| 5 | Verification specific | PASS | Concrete commands for each verification |
| 6 | Rollback complete | PASS | Remove config, plugin, stop server — no data loss |
| 7 | Archive plan | PASS | Trivial — no delta specs, openspec archive + commit |
| 8 | Plugin copy reliable | PASS | curl raw GitHub for 3 small files — reliable |

## 8-Edge Alignment Matrix

| Edge | Status | Evidence |
|------|--------|----------|
| Spec <-> Code | PASS | skip_specs: true, no spec delta |
| Spec <-> Docs | PASS | Why/What sections present |
| Spec <-> Tests | PASS | N/A (config change) |
| Code <-> Tests | PASS | N/A (config change) |
| Code <-> Docs | PASS | design.md matches approach |
| Code <-> Skills | PASS | Phase 5 updates skill |
| Docs <-> Skills | PASS | Phase 5 updates skill |
| Skills <-> Specs | PASS | developer-memory spec aligned |

## vars() Serialization Error

**Persistent issue:** 2 out of 5 reviewers still hit `vars() argument must have __dict__ attribute` even with inline context and increased iterations. This confirms the root cause is in the provider/LLM layer, not in the delegation pattern. The fix in `conversation_loop.py:2631` addresses the symptom but the actual error may be in the provider's response serialization during the summary call.

**Impact:** 60% success rate (3/5) with inline context, up from 0% with file paths. Further improvement requires the vars() fix to be applied and tested.

## Archive Readiness

**READY FOR ARCHIVE.** All 5 lenses PASS. No CRITICAL findings.
