# Proposal

## Why
Multi-turn coding agents and advisors targeting `gemini-4-argon*` (`gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`) frequently fail with `503 Service temporarily unavailable: all targets were skipped by pre-dispatch filters (ALL_TARGETS_SKIPPED)` because upstream OmniRoute (`v3.8.52`) omits `gemini-4-*` from `isGeminiTrailingModelTurnRejectingModel`, causing Google Cloud Code to return `HTTP 400 ("Requests ending with a model turn are not supported")`, which `isModelScoped400` falsely classifies as an unsupported-model error and `lockModelIfPerModelQuota` escalates into a 1-hour `family:gemini` lockout across both entitled Ultra `agy` accounts. Additionally, our container override lacks upstream's recommended `OMNIROUTE_SQLITE_SLOW_MS=200` synchronous SQLite stall diagnostic.

## What Changes
- **Strip Trailing Model Turns on `gemini-4-*` (`isGeminiTrailingModelTurnRejectingModel`)**: Extend the untracked `scripts/container-entrypoint-compat.sh` runtime normalization to widen `/^gemini-(?:3(?:\.\d+)?(?:-[a-z0-9-]+)?|pro-agent)$/` to `/^gemini-(?:[34](?:\.\d+)?(?:-[a-z0-9-]+)?|pro-agent)$/` in `/app/.build/next/server/chunks/{7449,37174}.js` so `stripTrailingGeminiModelTurns()` removes trailing `role: "model"` turns before dispatching `gemini-4-argon*` requests to Cloud Code.
- **Prevent False 1-Hour `model_capacity` Lockouts & Scope `agy` Lockouts to Exact Model**: Extend `scripts/container-entrypoint-compat.sh` across `/app/.build/next/server/chunks/*.js` (`32946.js` and `55661.js`) using negative lookahead `\bmodel(?!\s+turn\b)` so neither `isModelScoped400` nor `isProviderModelUnsupported400` matches request-shape `"model turn"` 400 errors, and ensure `lockModelIfPerModelQuota` treats `"agy"` identically to `"antigravity"` (`lockExactModel` instead of poisoning `family:gemini`).
- **SQLite Slow Query Telemetry & Semantic Cache Bridge Alignment**: Enable `OMNIROUTE_SQLITE_SLOW_MS=200` in `~/Omniroute/docker-compose.override.yml` per upstream `docs/ops/SQLITE_RUNTIME.md`, and align `PATCH /api/settings/database` `.cache` (`semanticCacheMaxSize: 1000`, `semanticCacheTTL: 18000000`) with `/api/settings` so `semanticCacheDbBridge.ts` uses the unified 5-hour TTL and 1,000-entry ceiling.
## Capabilities

### New Capabilities
<!-- None: aligning existing capabilities -->

### Modified Capabilities
- `omniroute-compression-and-routing`: Adds specifications for `gemini-4-*` trailing model turn stripping, false-positive `model turn` 400 lockout immunity across `isModelScoped400` and `isProviderModelUnsupported400`, exact-model lockout scoping on `agy`, slow SQLite event loop stall telemetry (`OMNIROUTE_SQLITE_SLOW_MS=200`), and unified database semantic cache settings (`semanticCacheMaxSize: 1000`, `semanticCacheTTL: 18000000`).

## Impact
- **Runtime & Deployment**: `~/Omniroute/docker-compose.override.yml` adds `OMNIROUTE_SQLITE_SLOW_MS=200`; `~/Omniroute/scripts/container-entrypoint-compat.sh` normalizes `gemini-4-*` trailing turn stripping and `agy` exact-model lockout scoping while keeping `~/Omniroute` git-tracked files 100% clean.
- **Combos, Routing & Caching**: Eliminates false 1-hour `family:gemini` lockouts (`503 ALL_TARGETS_SKIPPED`) on `gemini-4-argon*` combos, verifies zero-downtime lockout clearing via `DELETE /api/resilience/model-cooldowns`, and unifies `.cache` settings in `/api/settings/database` with `/api/settings`.
- **Non-Goals**:
  - Do NOT configure `auto/subscription` (upstream `CONNECTION_BILLING_CATALOG` omits `agy`/`github`/`muse-code`, `freeTierCatalog.ts` marks `agy` as `tos: "avoid"`, and cold-cache `admitUnknownQuota: false` fails closed on the first request).
  - Do NOT duplicate `stop_grace_period: 40s` in `docker-compose.override.yml` (already inherited from `x-common` in `docker-compose.yml:L40`, verified live as `StopTimeout=40`).
  - Do NOT switch `/app/data` to a host bind-mount (violates macOS VirtioFS WAL corruption guardrail) or enable `STREAM_RECOVERY_ENABLED=true` / `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED=true` / `caveman`.
