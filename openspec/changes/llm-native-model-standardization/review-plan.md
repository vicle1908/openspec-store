# Plan Review: llm-native-model-standardization (v3 — 6-Provider)

**Reviewed:** 2026-08-07T02:10:00+07:00
**Providers:** Claude Code, Antigravity, fable-5 Code, OpenCode, Pi, Codex

## Review Summary

| # | Provider | Lens | Verdict | Status |
|---|----------|------|---------|--------|
| 1 | **Claude Code** | Security + Architecture | ✅ APPROVED_WITH_FINDINGS | 3 findings |
| 2 | **Antigravity** | Code Quality + Tests | ❌ NOT_REVIEWED | Didn't follow instruction |
| 3 | **fable-5 Code** | Product Scope | ❌ NOT_REVIEWED | Binary not found (`fable-5` vs `kimi`) |
| 4 | **OpenCode** | Cross-cutting | ❌ NOT_REVIEWED | Permission denied (/tmp) |
| 5 | **Pi** | Security + Deployment | ✅ APPROVED_WITH_FINDINGS | 8 findings (2 HIGH, 3 MEDIUM, 3 LOW) |
| 6 | **Codex** | Spec Compliance | ❌ NOT_REVIEWED | WebSocket disabled |

**Effective reviews: 2/6** (Claude Code + Pi)

## Findings Summary

### HIGH Severity (must fix before execution)

| # | Finding | Source | Action |
|---|---------|--------|--------|
| H1 | `fallback_on=(Exception,)` too broad — includes auth errors | Pi | Use `FALLBACK_EXCEPTIONS` tuple (already designed) |
| H2 | `api_key` could leak via yaml `model_dump()` | Pi | Add yaml-level stripping or validator |

### MEDIUM Severity (fix during implementation)

| # | Finding | Source | Action |
|---|---------|--------|--------|
| M1 | Config naming inconsistency (ModelSettings vs model:) | Pi | Unify naming across all artifacts |
| M2 | `gateway_required` removal lacks replacement validation | Pi | Add `model_required` or implicit check |
| M3 | No atomic commit strategy for 3-repo migration | Pi | Specify atomic commit or compatibility shim |
| C1 | SecretStr/env var ordering | Claude Code | Verify env resolution order |
| C2 | `fallback_on` tuple needs explicit exception list | Claude Code | Use `FALLBACK_EXCEPTIONS` |
| C3 | 16 specs referenced but never enumerated | Claude Code | Add Phase 7 task list with spec paths |

### LOW Severity (cleanup)

| # | Finding | Source | Action |
|---|---------|--------|--------|
| L1 | `GatewayError` removal undocumented | Pi | Decide keep/remove, update catch sites |
| L2 | Env var prefix change undocumented | Pi | Document new `env_prefix` |
| L3 | No production monitoring plan | Pi | Add Phase 7 monitoring section |

## Positive Findings (confirmed by both reviewers)

| Area | Verdict |
|------|---------|
| SecretStr for api_key | ✅ `exclude=True` prevents serialization |
| Regex validation | ✅ Prevents injection via malformed model strings |
| SDK surface cleanup | ✅ Complete — all 3 repos covered |
| Cross-repo coverage | ✅ All consumer files enumerated |
| Line count accounting | ✅ ~1,432 removed, ~100 added |
| Test plan | ✅ 10 real LLM verification tests |
| Rollback | ✅ `git revert` with empty prior config |
| Deployment order | ✅ Correct dependency chain |

## CLI Agent Issues

| Agent | Issue | Fix |
|-------|-------|-----|
| Antigravity | Explained `--dangerously-skip-permissions` instead of reviewing | Prompt needs to be more explicit about reading the file |
| fable-5 | Binary is `kimi`, not `fable-5` | Use `fable-5 --auto -p` |
| OpenCode | Permission denied for `/tmp/*` | Copy context to working dir or use `-f` flag |
| Codex | WebSocket disabled (`websocket_disabled`) | Provider config issue — needs websocket transport |

## Verdict

**APPROVED_WITH_FINDINGS** — 2 successful reviews, both APPROVED_WITH_FINDINGS.

**Must fix before execution:**
1. H1: Use `FALLBACK_EXCEPTIONS` tuple (already designed, just ensure it ships)
2. H2: Add yaml-level api_key stripping

**Can fix during implementation:**
3. M1-M3: Config naming, validation, commit strategy
4. C1-C3: Env ordering, fallback exceptions, spec enumeration
5. L1-L3: GatewayError, env prefix, monitoring

**Estimated remediation:** ~2 hours total
