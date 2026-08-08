# Plan Review: llm-native-model-standardization (Multi-Provider)

**Reviewed:** 2026-08-12
**Providers:** Hermes (orchestrator), Claude Code (security), Antigravity (architecture), fable-5 Code (quality & tests), Codex (FAILED — auth expired)
**Change:** Replace custom gateway/resilience/budget layers (~1,432 lines) with native pydantic-ai infer_model() + FallbackModel

---

## Provider Status

| Provider | Role | Status | Findings | Runtime | Cost |
|----------|------|--------|----------|---------|------|
| Hermes | Orchestrator + Spec Compliance | ✅ | 6 gaps | inline | — |
| Claude Code | Security | ✅ | 7 findings | 80s | $0.14 |
| Antigravity | Architecture | ✅ | 5 recommendations | 91s | — |
| **fable-5 Code** | **Quality & Tests** | ✅ | **17 findings** | **~90s** | **—** |
| Codex | Quality & Tests (backup) | ❌ FAILED | — | — | — |

---

## Merged Alignment Matrix

| Edge | Status | Providers | Key Evidence |
|------|--------|-----------|-------------|
| Spec ↔ Code | PARTIAL | Hermes, Claude | 16 spec files need updates; GatewayError sites incomplete |
| Code ↔ Docs | PARTIAL | Claude, Hermes | design.md accurate but _ai/hooks.py, sdk/memory.py, cli/health_cmd.py missing |
| Docs ↔ Skills | FAIL | Hermes, Antigravity | agent-core AGENTS.md references LLMGateway |
| Skills ↔ Specs | PASS | Hermes | No skill files reference gateway/resilience types |
| Spec ↔ Docs | PARTIAL | Claude | Tasks.md Phase 7 lists 16 specs but only 3 named |
| Code ↔ Skills | FAIL | Antigravity | sdk/__init__.py removal breaks agent-docs-sync + agent-harness |
| Spec ↔ Tests | FAIL | **fable-5** | **3 CRITICAL gaps: tests/resilience/ not deleted, 60+ tests replaced by 10, agent-docs-sync resilience tests not deleted** |
| Code ↔ Tests | FAIL | **fable-5** | **13+ test files need gateway→model mock migration across 3 repos** |
| Knowledge ↔ Code | FAIL | Hermes, fable-5 | _ai/hooks.py, sdk/memory.py, cli/health_cmd.py, cli/config_cmd.py not addressed |

---

## Claude Code — Security Lens (7 Findings)

### S1 — base_url credential leakage (LOW)
ModelSettings protects api_key with SecretStr but base_url is plain str. If URL embeds creds (user:pass@host), they leak in repr/logs/traces.
**Fix:** Use SecretStr for base_url or add __repr_args__ override.

### S2 — GatewayError catch block incomplete (HIGH)
5 sites claimed but only 4 enumerated (agent_cmd.py ×4, agent.py ×1). Missing: foundation/__init__.py re-export + foundation/errors.py definition.
**Fix:** Add `grep -r "GatewayError"` verification in Phase 6. Remove from foundation/errors.py and foundation/__init__.py.

### S3 — FALLBACK_EXCEPTIONS auth error propagation (MEDIUM)
Excluding auth errors from fallback is correct. But spec doesn't define what handles the exception after FallbackModel rejects it.
**Fix:** Define sanitized error propagation. Add 401/403 test case.

### S4 — SDK re-export removal breaks downstream (HIGH)
Removing LLMGateway, ResilientGateway etc from sdk/__init__.py is breaking. agent-docs-sync imports 4 of these types; agent-harness imports 1.
**Fix:** Add DeprecationWarning shim or atomic deployment of all 3 repos.

### S5 — BudgetTracker USD cost ceiling loss (HIGH)
UsageLimits only tracks tokens, not dollars. Removing USD cost enforcement is a critical governance gap.
**Fix:** Keep minimal cost tracker OR document infrastructure-level cost governance.

### S6 — GATEWAY_ to MODEL_ env prefix (MEDIUM)
Env vars using GATEWAY_ prefix will be silently ignored after migration.
**Fix:** Declare new env_prefix explicitly. Add migration step. Use extra="forbid".

### S7 — Model format regex injection (MEDIUM)
infer_model() receives raw strings. No validation shown.
**Fix:** Add strict regex `^[a-z0-9-]+:[a-zA-Z0-9._-]+$`. Add adversarial test cases.

---

## Antigravity — Architecture Lens (5 Recommendations)

### A1 — Fix Resilience Gaps
Update FALLBACK_EXCEPTIONS to catch ModelAPIError and standard provider status codes.

### A2 — Unify Model Creation
Expose create_model and create_fallback_model directly from agent_core.sdk.

### A3 — Pass Custom Endpoint Settings
Ensure create_model() receives ModelSettings to forward base_url, api_key, and timeout_seconds.

### A4 — Soft Deprecate SDK & Config
Add env aliases for GATEWAY_* variables and temporary parameter aliases in build_agent().

### A5 — Update Skill Contracts
Update contracts.py in agent-harness to reference model instead of gateway.

---

## fable-5 Code — Quality & Tests Lens (17 Findings)

### CRITICAL (3)

**F1: tests/resilience/ not listed for deletion**
Plan deletes resilience/ source (~411 lines) but never mentions tests/resilience/ (3 files, 373 lines, 22 tests). These will immediately break with ModuleNotFoundError.
**Fix:** Add to deletion list. Create equivalent tests if behavior preserved.

**F2: agent-docs-sync resilience tests not listed**
agent-docs-sync/tests/test_resilience.py (193 lines, 14 tests) imports from agent_core.resilience. Not mentioned anywhere.
**Fix:** Add to deletion list or Phase 5.

**F3: 60+ unit tests replaced by 10 integration tests**
Old: 68 test functions covering thread safety, state machine transitions, error codes, retry predicates. New: 10 real-LLM verification tests. Net loss of ~58 tests.
**Fix:** Expand test_model_loading.py from 10 to ≥25 tests. Target ≥667 agent-core tests post-migration.

### HIGH (5)

**F4: _ai/hooks.py BudgetTracker import not addressed**
_ai/hooks.py imports get_budget_tracker from llm_gateway at lines 16 and 35. Not in any task phase. Will break on import when llm_gateway/ is deleted.
**Fix:** Add _ai/hooks.py to Phase 2.

**F5: sdk/memory.py gateway references not addressed**
sdk/memory.py:368 reads _settings.gateway.litellm_url and _settings.gateway.bifrost_url. After migration, settings.gateway won't exist.
**Fix:** Add sdk/memory.py to task list.

**F6: cli/health_cmd.py and cli/config_cmd.py not addressed**
health_cmd.py reads settings.gateway fields; config_cmd.py hardcodes "gateway" key. Neither mentioned.
**Fix:** Add both to Phase 2.

**F7: foundation/errors.py GatewayError class not addressed**
GatewayError defined in foundation/errors.py, re-exported from foundation/__init__.py. Never mentioned for deletion.
**Fix:** Add removal to task list. Update tests/foundation/test_errors.py.

**F8: agent-docs-sync 8 test files need gateway→model migration**
8 test files with gateway mock/fixture patterns will break. None enumerated in plan.
**Fix:** Add explicit task items for each of the 8 test files.

### MEDIUM (9)

**F9: agent-harness 5 test files need StubGateway→Model migration**
StubGateway(LLMGateway) pattern used in 5 test files. Not listed.
**Fix:** Add to Phase 4 or Phase 5.

**F10: Budget exceeded → RunReason mapping not specified**
agent_base/agent.py:370 checks e.code == "budget_exceeded" to set RunReason. No mapping documented for UsageLimitExceeded.
**Fix:** Document exception-to-RunReason mapping.

**F11: Invalid model ID error handling missing**
create_model() has no try/except. Old create_gateway() raised GatewayError with structured code.
**Fix:** Wrap infer_model() with domain-appropriate error handling.

**F12: FallbackModel empty fallback list edge case**
If fallback_ids is empty, FallbackModel may behave unexpectedly. Old FallbackChain rejected empty lists.
**Fix:** Add guard: if not fallback_ids: return infer_model(primary_id).

**F13: FallbackModel fallback_on API not verified**
Plan assumes fallback_on parameter exists on FallbackModel. Not confirmed.
**Fix:** Verify pydantic-ai v2 FallbackModel API before implementation.

**F14: Coverage regression — net line delta**
Deleting ~835 lines of tests, adding ~100 lines of source. Net loss.
**Fix:** Maintain ≥667 agent-core tests, ≥222 agent-docs-sync tests.

**F15: tests/cli/test_cli.py GatewayError mock needs update**
2 monkeypatches raise GatewayError. Not mentioned.
**Fix:** Update to raise ModelAPIError instead.

**F16: tests/agent_base/test_agent.py and tests/sdk/test_agents.py need mock updates**
Both create mock gateways. After migration: mock models.
**Fix:** Add to Phase 5.

**F17: No import sweep validation method specified**
Phase 6 says "no remaining imports" but no grep command defined.
**Fix:** Add explicit grep command in Phase 6.

---

## Hermes — Orchestrator Gaps (6)

1. **foundation/errors.py** — GatewayError class not mentioned for removal
2. **foundation/__init__.py** — GatewayError re-export not mentioned
3. **_ai/hooks.py** — TWO BudgetTracker references need rewriting
4. **agent-docs-sync config.py** — RuntimeConfigLike protocol replacement unspecified
5. **agent-harness stages/contracts.py** — gateway_required removal not shown
6. **pyproject.toml** — pydantic-ai version bump may need updates across repos

---

## Antigravity — Additional Actions (5)

1. Update FALLBACK_EXCEPTIONS to catch ModelAPIError + provider status codes
2. Expose create_model/create_fallback_model from agent_core.sdk
3. Pass ModelSettings to create_model() for custom endpoints
4. Add GATEWAY_* env aliases + build_agent() parameter aliases
5. Update contracts.py to reference model instead of gateway

---

## Blocking Recommendations (Must Resolve Before Phase 2)

| # | Priority | Finding | Action |
|---|----------|---------|--------|
| 1 | **CRITICAL** | tests/resilience/ not deleted (F1) | Add to deletion list; 22 tests will break immediately |
| 2 | **CRITICAL** | agent-docs-sync resilience tests not deleted (F2) | Add test_resilience.py to deletion list |
| 3 | **CRITICAL** | 60+ tests replaced by 10 (F3) | Expand to ≥25 tests; target ≥667 agent-core tests |
| 4 | **CRITICAL** | BudgetTracker USD cost ceiling (S5) | Define cost governance replacement |
| 5 | **HIGH** | _ai/hooks.py not addressed (F4) | Add to Phase 2; rewrite budget hooks |
| 6 | **HIGH** | sdk/memory.py not addressed (F5) | Add to task list |
| 7 | **HIGH** | cli/health_cmd.py + config_cmd.py (F6) | Add to Phase 2 |
| 8 | **HIGH** | GatewayError class not deleted (S2+F7) | Remove from foundation/errors.py, foundation/__init__.py |
| 9 | **HIGH** | 13+ test files need mock migration (F8+F9+F15+F16) | Enumerate all in Phase 5 |
| 10 | **HIGH** | Codex auth expired | Run `codex login` |
| 11 | **MEDIUM** | Auth error propagation (S3) | Define sanitized error path |
| 12 | **MEDIUM** | GATEWAY_ → MODEL_ env prefix (S6) | Declare new prefix; add mapping |
| 13 | **MEDIUM** | FallbackModel fallback_on not verified (F13) | Verify pydantic-ai API |
| 14 | **MEDIUM** | Model format validation (S7) | Add regex + adversarial tests |
| 15 | **LOW** | base_url credential leak (S1) | Use SecretStr or __repr_args__ |
