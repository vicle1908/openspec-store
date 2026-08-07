# Plan Review: llm-native-model-standardization (Multi-Provider)

**Reviewed:** 2026-08-12
**Providers:** Hermes (inline orchestrator), Claude Code (security), Antigravity (architecture), Codex (quality — FAILED)
**Change:** Replace custom gateway/resilience/budget layers (~1,432 lines) with native pydantic-ai infer_model() + FallbackModel

---

## Provider Status

| Provider | Role | Status | Output |
|----------|------|--------|--------|
| Hermes | Orchestrator + Spec Compliance | ✅ Full review | Inline (see below) |
| Claude Code | Security | ✅ 7 findings, $0.14 | 80s runtime |
| Antigravity | Architecture | ✅ 5 recommendations | 91s runtime |
| Codex | Quality & Tests | ❌ FAILED | Cockpit proxy 400 + API key expired (401) |

---

## Merged Alignment Matrix

| Edge | Status | Providers | Key Evidence |
|------|--------|-----------|-------------|
| Spec ↔ Code | PARTIAL | Hermes, Claude | 16 spec files need updates; GatewayError sites incomplete (4/5 enumerated) |
| Code ↔ Docs | PARTIAL | Claude, Hermes | design.md accurate; _ai/models.py has 3 redundant factories → design correctly simplifies |
| Docs ↔ Skills | FAIL | Hermes, Antigravity | agent-core AGENTS.md references LLMGateway in uv practices section |
| Skills ↔ Specs | PASS | Hermes | No skill files reference gateway/resilience types directly |
| Spec ↔ Docs | PARTIAL | Claude | Tasks.md Phase 7 lists 16 specs but only 3 named |
| Code ↔ Skills | FAIL | Antigravity | sdk/__init__.py removal breaks agent-docs-sync + agent-harness imports |
| Spec ↔ Tests | UNKNOWN | Codex (failed) | 10 new tests proposed; 269 lines deleted — coverage gap unverified |
| Code ↔ Tests | UNKNOWN | Codex (failed) | agent-harness tests timeout (>180s) — pre-existing |
| Knowledge ↔ Code | PASS | Hermes | GitNexus indexed; no cross-module impact beyond 3 repos |

---

## Claude Code — Security Lens (7 Findings)

### S1 — base_url credential leakage (LOW)
ModelSettings protects api_key with SecretStr but base_url is plain str. If URL embeds creds (user:pass@host), they leak in repr/logs/traces.
**Fix:** Use SecretStr for base_url or add __repr_args__ override.

### S2 — GatewayError catch block incomplete (HIGH)
5 sites claimed but only 4 enumerated (agent_cmd.py ×4, agent.py ×1). Missing: foundation/__init__.py re-export + foundation/errors.py definition.
**Fix:** Add `grep -r "GatewayError"` verification in Phase 6. Remove from foundation/errors.py and foundation/__init__.py.

### S3 — FALLBACK_EXCEPTIONS auth error propagation (MEDIUM)
Excluding auth errors from fallback is correct. But spec doesn't define what handles the exception after FallbackModel rejects it. Unhandled auth errors could leak sensitive trace info.
**Fix:** Define sanitized error propagation. Add 401/403 test case.

### S4 — SDK re-export removal breaks downstream (HIGH)
Removing LLMGateway, ResilientGateway etc from sdk/__init__.py is breaking. agent-docs-sync imports 4 of these types; agent-harness imports 1. No deprecation shim.
**Fix:** Add DeprecationWarning shim or atomic deployment of all 3 repos.

### S5 — BudgetTracker USD cost ceiling loss (HIGH → CRITICAL)
UsageLimits only tracks tokens, not dollars. Removing USD cost enforcement is a critical governance gap — runaway costs, prompt injection attacks, fallback cascade charges.
**Fix:** Keep minimal cost tracker OR document infrastructure-level cost governance.

### S6 — GATEWAY_ to MODEL_ env prefix (MEDIUM)
Env vars using GATEWAY_ prefix will be silently ignored after migration. Could route sensitive data to wrong endpoint via default fallback.
**Fix:** Declare new env_prefix explicitly. Add migration step. Use extra="forbid".

### S7 — Model format regex injection (MEDIUM)
infer_model() receives raw strings. No validation shown. Malicious model strings could cause header injection, path traversal, or SSRF.
**Fix:** Add strict regex `^[a-z0-9-]+:[a-zA-Z0-9._-]+$`. Add adversarial test cases.

---

## Antigravity — Architecture Lens (5 Recommendations)

### A1 — Fix Resilience Gaps
Update FALLBACK_EXCEPTIONS in _ai/models.py to catch ModelAPIError and standard provider status codes. Current tuple (ConnectionError, TimeoutError, OSError) misses HTTP-level errors.

### A2 — Unify Model Creation
Expose create_model and create_fallback_model directly from agent_core.sdk. Consumer repos (agent-docs-sync, agent-harness) should import from SDK, not internal _ai package.

### A3 — Pass Custom Endpoint Settings
Ensure create_model() receives ModelSettings to forward base_url, api_key, and timeout_seconds to underlying providers. Current design doesn't show how custom endpoints propagate.

### A4 — Soft Deprecate SDK & Config
Add env aliases for GATEWAY_* variables and temporary parameter aliases in build_agent(). Even with "no backward compat" intent, a transition period prevents production breaks.

### A5 — Update Skill Contracts
Update contracts.py in agent-harness and skill instructions to reference model instead of gateway. stages/contracts.py has gateway_required field that must change.

---

## Hermes — Inline Orchestrator Review

### Migration Completeness Gaps

1. **foundation/errors.py** — GatewayError class defined here; tasks don't explicitly mention removing it
2. **foundation/__init__.py** — Re-exports GatewayError; needs removal
3. **_ai/hooks.py** — TWO BudgetTracker references (pre_check + check_and_record); task says "remove import" but both hook methods need rewriting
4. **agent-docs-sync config.py** — RuntimeConfigLike protocol removal not specified what replaces it
5. **agent-harness stages/contracts.py** — gateway_required removal not shown with new validation logic
6. **All repos: pyproject.toml** — Not listed but pydantic-ai version bump may need updates

### Task Numbering
Two Task 2.7 entries exist (sdk/__init__.py and sdk/agents.py). Renumber to avoid confusion.

---

## Blocking Recommendations (Must Resolve Before Phase 2)

| # | Priority | Finding | Action |
|---|----------|---------|--------|
| 1 | CRITICAL | BudgetTracker removal | Define cost governance replacement or document infrastructure-level delegation |
| 2 | HIGH | GatewayError incomplete | Enumerate all 5+ sites; add grep verification |
| 3 | HIGH | SDK breaking change | Atomic deployment of all 3 repos OR deprecation shim |
| 4 | HIGH | Codex auth expired | Run `codex login` to refresh credentials before next review |
| 5 | MEDIUM | Auth error propagation | Define sanitized error path through FallbackModel |
| 6 | MEDIUM | Env prefix migration | Declare new prefix; add GATEWAY_* mapping step |
| 7 | MEDIUM | Model format validation | Add regex validator + adversarial tests |
| 8 | LOW | base_url credential leak | Use SecretStr or __repr_args__ override |

---

## Codex Failure Details

**Error chain:**
1. Cockpit Tools proxy websocket: `400 Bad Request` at ws://localhost:51006/v1/responses
2. Fallback to direct API: `401 Unauthorized` — API key `agt_code***5E6u` is expired
3. Both websocket and HTTPS transports fail → no output produced

**Resolution:** User must run `codex login` to refresh credentials. The Cockpit Tools websocket incompatibility is an upstream issue (GitHub #6408) that doesn't block HTTPS fallback once auth is valid.
