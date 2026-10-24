# Design

## Context

See `proposal.md` for motivation. Inspection of `/app/data/storage.sqlite` (`692.74 MB`), `/app/data/call_logs/` (`1.38 GB`), `open-sse/handlers/chatCore.ts:1512-1522`, and `open-sse/services/combo/executeTargetAttempt.ts:173-284` identified three zero-code configuration optimizations that reclaim >1.5 GB of volume space, activate server-side tool-result compression for headerless clients, and protect combos from high-latency or permanently banned OAuth seats.

## Goals / Non-Goals

**Goals:**
- Configure `/api/settings/database` (`PATCH`) with bounded retention (`conversationTurnNodes: 2`, `usageHistory: 30`, `quotaSnapshots: 3`, `callLogs: 7`, `compressionAnalytics: 7`, `compressionCacheStats: 7`, `xpAuditLog: 7`, `domainCostHistory: 14`), `aggregation: {"enabled": true, "rawDataRetentionDays": 7}`, and `backup: {"autoBackupEnabled": true, "autoBackupFrequency": "daily", "keepLastNBackups": 2}`, and add `CALL_LOG_MAX_ENTRIES=2000`, `CHAT_LOG_MAX_BODY_KB=256`, `CALL_LOGS_TABLE_MAX_ROWS=25000`, and `PROXY_LOGS_TABLE_MAX_ROWS=25000` to `~/Omniroute/docker-compose.override.yml`.
- Update `PUT /api/context/combos/default-caveman` and `PUT /api/settings/compression` so `engines.caveman.enabled: false`, `cavemanConfig.enabled: false`, `compressionComboId: "default-caveman"`, and `stackedPipeline: [{"engine": "session-dedup"}, {"engine": "lite"}, {"engine": "rtk", "intensity": "minimal"}, {"engine": "codex-responses"}, {"engine": "headroom"}]` execute automatically on all headerless requests.
- Enable `zeroLatencyOptimizationsEnabled: true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) in `/api/settings/combo-defaults` and `agy` combo configs, set `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED: "false"` so 2-account `gemini-4-argon*` pools do not reject concurrent subagent streams with `503 POOL_BUSY`, and enable `/api/settings/auto-disable-accounts` (`{"enabled": true, "scope": "subscription", "threshold": 3}`).

**Non-Goals:**
- Enabling speculative hedging (`hedging: true`), which duplicates upstream token spend.
- Running blocking `VACUUM` (`auto_vacuum = INCREMENTAL` reclaims freed pages via bounded `reclaimFreedPages()` batches).
- Modifying tracked files in `/Users/androidteam/Omniroute`.

## Decisions

1. **Server-Side Tool-Safe Stack via `compressionComboId: "default-caveman"` and `caveman: false` (`open-sse/handlers/chatCore.ts:1512-1522`)**
   - *Rationale*: In `chatCore.ts:1512-1522`, `config.stackedPipeline` is only overwritten by the `applyLossyRequestPolicy`-downgraded `compressionPlan.stackedPipeline` when `!compressionComboApplied && !config.compressionComboId`. By disabling `caveman` (`engines.caveman.enabled: false`, `cavemanConfig.enabled: false` so user and assistant prose is never touched) and setting `compressionComboId: "default-caveman"` with `stackedPipeline: [{"engine": "session-dedup"}, {"engine": "lite"}, {"engine": "rtk", "intensity": "minimal"}, {"engine": "codex-responses"}, {"engine": "headroom"}]` (matching the updated `default-caveman` row in `compression_combos`), `!config.compressionComboId` evaluates to `false` and `applyStackedCompressionAsync` executes all 5 tool-safe engines on every headerless turn across `/v1/chat/completions`, `/v1/messages`, and `/v1/responses`.

2. **Database Retention & Call-Log Artifact Caps (`src/lib/db/cleanup.ts`, `src/lib/usage/callLogRotation.ts`)**
   - *Rationale*: `conversation_turn_nodes` (`263.18 MB`), `usage_history` (`106.41 MB`), `quota_snapshots` (`93.58 MB`), and `call_logs` (`67.65 MB` + `1.38 GB` in `/app/data/call_logs/`) account for >85% of total volume usage. Lowering retention bounds, enabling `aggregation.enabled: true` (so `cleanupUsageHistory` rolls up >30d rows into `daily_usage_summary`), and setting `CALL_LOG_MAX_ENTRIES=2000` / `CHAT_LOG_MAX_BODY_KB=256` lets `rotateCallLogs()` and `runAutoCleanup()` + `reclaimFreedPages()` reclaim >1.5 GB without blocking the event loop.

3. **Predictive TTFT Circuit Breaker (`predictiveTtftMs: 25000`, `fallbackCompressionMode: "off"`), `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED: "false"`, & Subscription Ban Auto-Disable (`executeTargetAttempt.ts:173-195,256-283`, `antigravityLeaseLifecycle.ts:103-119`, `autoDisableBannedAccount.ts:16-60`)**
   - *Rationale*: Live `/api/combos/metrics` showed connection `38782750-7a60-46d4-ae3f-e8c13cda296b` (`vicgnome19096@gmail.com`) had an average latency of `73,366 ms` (`8/9` failures). Keeping all 15 `agy` accounts in `gemini-3.8-flash-high` (`models=15`) and all 8 Opus accounts in `claude-opus-5.5` (`models=9`) while setting `zeroLatencyOptimizationsEnabled: true`, `predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, and `fallbackCompressionMode: "off"` causes `executeTargetAttempt.ts:173-195` to skip any target whose historical `avgLatencyMs > 25000` on attempt `0` (`predictive_ttft`) while preserving canonical combo membership. Setting `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED: "false"` prevents `buildAntigravityPoolBusyResponse` (`503 All eligible Antigravity accounts are currently handling a request for this model`) when 3+ concurrent subagents share the 2-account `gemini-4-argon` pool, and setting `auto-disable-accounts` to `{"enabled": true, "scope": "subscription", "threshold": 3}` stamps `banDisabledAt` on permanently banned OAuth seats.

## Risks / Trade-offs

- **Risk**: Recreating `omniroute-base` to apply the 4 `CALL_LOG_*` / `CHAT_LOG_*` / `PROXY_LOGS_*` environment variables in `docker-compose.override.yml` briefly restarts the container (~5s).
  - *Mitigation*: Acquire `/usr/bin/lockf` on `~/.omniroute/update.lock` before `docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base` and run `~/Omniroute/scripts/ensure-muse-wire-compat.sh omniroute` immediately after healthcheck passes.
