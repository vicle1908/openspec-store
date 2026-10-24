# Design

## Context
See `proposal.md` — Why. Live container telemetry (`GET /api/rate-limits` and `docker logs omniroute` at `2026-10-24T11:28:21.700Z` / `11:28:26.053Z`) confirmed a 3-step failure chain causing `503 ALL_TARGETS_SKIPPED` on `gemini-4-argon*`:
1. `isGeminiTrailingModelTurnRejectingModel` (`open-sse/translator/helpers/geminiTrailingModelTurn.ts:L18`, compiled into `chunks/7449.js` and `chunks/37174.js`) matches `/^gemini-(?:3(?:\.\d+)?(?:-[a-z0-9-]+)?|pro-agent)$/`, omitting `gemini-4-*`. When an advisor or subagent sends a conversation ending on an assistant/model turn, `stripTrailingGeminiModelTurns()` is skipped and Google Cloud Code returns `HTTP 400: "Requests ending with a model turn are not supported."`
2. `isModelScoped400` (`open-sse/services/modelAccessDenied.ts:L10,L29`, compiled into `chunks/32946.js`) and `isProviderModelUnsupported400` (`open-sse/services/accountFallback.ts:L404`, compiled into `chunks/55661.js`) match `/\bmodel.*not.*(?:available|found|supported|accessible)\b/i` and `/\bmodel\b[\s\S]{0,80}?\bnot\s+supported\b/i` against `"...ending with a [model] turn are [not supported]"` (verified in `call_logs` IDs `d1284bad-2a92-47d8-8999-0c650395e3c8` and `c05ad91f-6975-4c09-ad9c-e095d29f5376`), causing `executeTargetAttempt.ts:L1043` to retry the unstripped payload on the second Ultra account and call `lockModelIfPerModelQuota(provider, connectionId, rawModel, "model_capacity", 3_600_000)` on both accounts.
3. `lockModelIfPerModelQuota` (`open-sse/services/accountFallback.ts:L975`, compiled into `chunks/32946.js`) checks `"antigravity" === getCanonicalLockProvider(provider)` (`"antigravity"===ag(a)`). Because `ag("agy")` returns `"agy"`, it falls back to `lockModel`, locking the entire `family:gemini` quota family on both Ultra accounts (`338764b8` and `0532bad4`) for 60 minutes, during which every subsequent `gemini-4-argon*` turn fails pre-dispatch with `503 ALL_TARGETS_SKIPPED`.

## Goals / Non-Goals

**Goals:**
- Normalize `isGeminiTrailingModelTurnRejectingModel`, `MODEL_ACCESS_DENIED_PATTERNS` / `isModelScoped400` / `isProviderModelUnsupported400`, and `lockModelIfPerModelQuota` in `~/Omniroute/scripts/container-entrypoint-compat.sh` so `gemini-4-argon*` strips trailing model turns and never suffers false 1-hour `family:gemini` lockouts.
- Enable `OMNIROUTE_SQLITE_SLOW_MS=200` in `~/Omniroute/docker-compose.override.yml` per upstream `docs/ops/SQLITE_RUNTIME.md` and align `PATCH /api/settings/database` `.cache` (`semanticCacheMaxSize: 1000`, `semanticCacheTTL: 18000000`) with `/api/settings`.
- Keep all git-tracked files in `~/Omniroute` strictly unmodified (`git status --untracked-files=no` clean).

**Non-Goals:**
- Modifying any git-tracked file in `~/Omniroute`.
- Adopting `auto/subscription` (rejected after review because `CONNECTION_BILLING_CATALOG` only includes `provider: "antigravity"`/`"claude"`/`"codex"` and excludes `"agy"`/`"github"`/`"muse-code"`, `freeTierCatalog.ts` marks `agy` as `tos: "avoid"`, and `resolveFreeAccessState` fails closed on cold cache).
- Duplicating `stop_grace_period: 40s` in `docker-compose.override.yml` (already inherited from `x-common` in `docker-compose.yml:L40`).

## Decisions

### 1. Normalize `gemini-4-*` Trailing Turn Stripping and `agy` Lockout Scoping in `container-entrypoint-compat.sh`
- **Decision**: Extend `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`--patch-only` aware, verified by `scripts/ensure-muse-wire-compat.sh` in `update.sh` Gate 4b and `omniroute-watchdog.sh`) to idempotently scan `/app/.build/next/server/chunks/*.js`:
  1. Replace `/\^gemini-\(\?:3\(\?:\\\.\(\\d\+\)\)\?/g` (`^gemini-(?:3(?:\.\d+)?`) with `^gemini-(?:[34](?:\.\d+)?` (`chunks/{7449,37174}.js`) so `isGeminiTrailingModelTurnRejectingModel` and `isAntigravityGeminiChatModel` return `true` for all `gemini-4-*` models.
  2. Replace `/\\bmodel\.\*not\.\*/g` with `\bmodel(?!\s+turn\b).*not.*` and `/\\bmodel\\b\[\\s\\S\]\{0,80\}\?\\b\(\?:not\\s\+supported/g` with `\bmodel(?!\s+turn\b)\b[\s\S]{0,80}?\b(?:not\s+supported` (`chunks/{32946,55661}.js`) so `"Requests ending with a model turn are not supported"` never triggers `isModelScoped400` or `isProviderModelUnsupported400`, and widen `"antigravity"===ag(a)?bz:ap` to `("antigravity"===ag(a)||"agy"===ag(a)?bz:ap)` (`chunks/32946.js`) so `agy` per-model lockouts call `lockExactModel` (`bz`).
- **Rationale**: Fixes all three links of the `503 ALL_TARGETS_SKIPPED` chain across all compiled server chunks without dirtying `~/Omniroute` git-tracked source files, while `DELETE /api/resilience/model-cooldowns` (`omni-resilience` / `cli-resilience`) provides zero-downtime lockout clearing.

### 2. Enable Upstream `OMNIROUTE_SQLITE_SLOW_MS=200` and Unify Database Semantic Cache Settings
- **Decision**: Add `- OMNIROUTE_SQLITE_SLOW_MS=200` to `services.omniroute-base.environment` in `~/Omniroute/docker-compose.override.yml`, and update `/api/settings/database` `.cache` to `{"semanticCacheMaxSize": 1000, "semanticCacheTTL": 18000000}` matching `/api/settings`.
- **Rationale**: Per `docs/ops/SQLITE_RUNTIME.md`, `better-sqlite3` executes synchronously on the Node.js event loop (`slowDiagnostics.ts`), emitting rate-limited (1 per 10s per adapter) `[SQLITE-SLOW]` warnings when a synchronous operation takes $\ge 200\text{ ms}$. In `src/lib/cache/semanticCacheDbBridge.ts`, the semantic cache resolver reads `getUserDatabaseSettings().cache`, so aligning `database_settings.cache` eliminates the 100-entry / 30-minute discrepancy against `/api/settings`.
- **Transaction Boundary**: `instrumentSqliteAdapter` wraps `prepare`, `run`, `get`, `all`, `exec`, `pragma`, `transaction`, `immediate`, and `checkpoint` in a `try/finally` that never masks transaction outcomes or errors, while `stop_grace_period: 40s` (inherited from `docker-compose.yml` `x-common`) preserves the 40-second `SIGTERM` drain boundary for in-flight WAL checkpoints.
## Risks / Trade-offs
- **Webpack chunk filenames in future upstream releases**: Mitigated by scanning `/app/.build/next/server/chunks/*.js` by content signature rather than hardcoded chunk numbers in `container-entrypoint-compat.sh`, failing open if upstream merges the regex fix natively.
- **Additional log lines on slow SQLite queries**: Rate-limited by `WARN_EVERY_MS = 10_000` in `slowDiagnostics.ts` and only triggers when a synchronous query exceeds `200ms`.
