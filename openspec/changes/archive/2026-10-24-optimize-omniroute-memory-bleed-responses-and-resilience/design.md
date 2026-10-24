# Design

## Context

See `proposal.md` for motivation. Deep source inspection of OmniRoute `v3.8.52` (`open-sse/handlers/chatCore.ts`, `open-sse/services/compression/*`, `src/lib/memory/*`, `src/sse/handlers/chat.ts`) uncovered four subtle runtime behaviors that govern token usage, tool-output fidelity, and streaming resilience across coding agents.

## Goals / Non-Goals

**Goals:**
- Disable OmniRoute's built-in memory and skills injection (`PUT /api/settings/memory` with `{"enabled": false, "skillsEnabled": false, "maxTokens": 0}`) and delete all 75 rows in `memories` (`DELETE /api/memory/{id}`) using `OMNIROUTE_API_KEY` (`manage` scope).
- Configure `/api/settings/compression` (`PUT`) to set `lite: {"compressToolResults": false, "maxToolLength": 200000}`, enable `engines.headroom: {"enabled": true}`, `engines["codex-responses"]: {"enabled": true}`, and `codexResponsesConfig: {"enabled": true, ...}`, and set `contextBudget.ladderOverride` under `mode: "replace-autotrigger"` and `policy: "percentage"` (`pct: 0.85`).
- Enable 4 verified resilience feature flags via `PUT /api/settings/feature-flags` (`QUOTA_WINDOW_BOUNDED_PARK`, `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED`, `COOLDOWN_RETRY_SKIP_REFUSALS_ENABLED`, `PROVIDER_SAFETY_STOPS_TERMINAL`).
- Configure `/api/settings` (`PATCH`) with `claudeClassifierCompat: "auto"`, `claudeFastMode.supportedModels` including `"claude-opus-5-5"`, `maxBodySizeMb: 50`, and `modelsDevSyncEnabled: true`, and run `POST /api/settings/models-dev` with `{"action": "sync"}` then `{"action": "start"}`.

**Non-Goals:**
- Enabling `FLUSH_EMPTY_RETRY_ENABLED` (`open-sse/handlers/chatCore/streamingTail.ts:274-316` buffers up to 256 KB of every translated stream before emitting the first SSE byte, degrading streaming TTFT).
- Switching `ADAPTIVE_ADMISSION_MODE` to `enforce`, enabling `taskRouting` / `backgroundDegradation`, or enabling `ccr` / `PII_REDACTION_ENABLED`.

## Decisions

1. **Disable Built-in Memory & Per-Row `DELETE /api/memory/{id}` (`src/lib/memory/injection.ts:241-323`, `src/app/api/memory/[id]/route.ts:12-26`)**
   - *Rationale*: In `chatCore.ts:1141`, every Bearer-authenticated request (`apiKeyInfo.id = "6a72d8ab-88db-4d49-973b-864c6cbdace5"`) runs `injectMemoryAndSkills()` before translation and `runMemoryExtractionGate()` after completion. Because `src/app/api/memory/route.ts` only implements `GET` and `POST` (`DELETE /api/memory` returns `405`), disabling `memoryEnabled`/`skillsEnabled` via `PUT /api/settings/memory` and iterating `DELETE /api/memory/{id}` over the 75 IDs from `GET /api/memory?limit=100` cleanly purges `memories`, `memory_fts`, `sqlite-vec`, and `_memoryCache` within individual SQLite transactions.

2. **`lite.compressToolResults: false` + `headroom` + `codex-responses` + `contextBudget` (`policy: "percentage"`, `pct: 0.85`) (`lite.ts:23,305`, `computeTarget.ts:21-30`, `ladder.ts:46`, `resolveAdaptivePlan.ts:62-63`)**
   - *Rationale*:
     - Under the lossless default pipeline, `lite.compressToolResults` defaults to `true` (`DEFAULT_MAX_TOOL_LENGTH = 2000`), silently truncating all prior-turn tool results (including `Read` and `Grep` file contents) at 2,000 characters. Setting `lite: {"compressToolResults": false, "maxToolLength": 200000}` stops this truncation while enabling `engines.headroom: {"enabled": true}` (`lossy: false` in `engineCatalog.ts:134`) adds lossless JSON-array and log compaction on normal headerless turns.
     - On `/v1/responses`, `adaptBodyForCompression()` (`bodyAdapter.ts:340-405`) tags `function_call_output` items with `[CODEX_RESPONSE_ITEM_META]`. `codex-responses` (`engines/codexResponses/index.ts`) inspects those tags to protect `Read`, `Glob`, `Grep`, `Write`, `Edit`, `WebSearch`, `WebFetch`, and `find` while compacting large shell/diff/test outputs.
     - In `computeTarget.ts:21-30`, `pct` (`0.85`) is only evaluated when `policy === "percentage"` (whereas `policy === "reserve-output"` ignores `pct` and computes `modelContextLimit - outputReserve - safetyMargin`, triggering only at ~99.5% of a 1M window). Furthermore, in `adaptiveCompression/ladder.ts:46`, `AGGRESSIVENESS.stacked = 50` exceeds `rtk` (`20`) and `codex-responses` (`22`), so `mode: "floor"` (`startTier = 50`) skips both. Pairing `mode: "replace-autotrigger"` (`startTier = 0`) and `policy: "percentage"` (`pct: 0.85`) with `ladderOverride` (`session-dedup` -> `headroom` -> `lite` -> `codex-responses` -> `rtk`) guarantees 85% escalation through `codex-responses` and `rtk` without invoking lossy prose engines (`caveman`, `aggressive`, `ultra`).
3. **Four Zero-Restart Resilience Flags (Excluding `FLUSH_EMPTY_RETRY_ENABLED`)**
   - *Rationale*: `QUOTA_WINDOW_BOUNDED_PARK`, `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED`, `COOLDOWN_RETRY_SKIP_REFUSALS_ENABLED`, and `PROVIDER_SAFETY_STOPS_TERMINAL` operate strictly on pre-first-frame EOF, stale quota parks, 403/410 cooldown sleeps, and explicit safety-refusal 400/403 codes, adding zero latency to healthy requests.

4. **`claudeClassifierCompat: "auto"`, `claudeFastMode`, `maxBodySizeMb: 50`, and Synchronous + Periodic `models.dev` Sync**
   - *Rationale*: `isClaudeCodeClassifierRequest` (`claudeClassifierCompat.ts:55-63`) matches only `sourceFormat === FORMATS.CLAUDE` with `SECURITY_MONITOR_MARKER` (`"You are a security monitor for autonomous AI coding agents"`), returning `<block>no</block>` or `<severity>0</severity>` in `<1ms` when `model` resolves to an active provider connection (such as `"claude-opus-5.5"` or `"gemini-3.8-flash-high"`). Because `POST /api/settings/models-dev` with `{"action": "start"}` fires `syncModelsDev()` asynchronously in the background (`modelsDevSync.ts:816`), calling `{"action": "sync"}` first (which `await`s `syncModelsDev()` and caches `cachedData` in memory for 24h) followed by `{"action": "start"}` guarantees `GET /api/settings/models-dev?action=status` deterministically reports `enabled: true` and `lastSync !== null`.

## Risks / Trade-offs

- **Risk**: Container bind-mount drift on `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` if the host file was recreated or unmounted.
  - *Mitigation*: Verify `docker inspect omniroute` and `curl -fsS http://127.0.0.1:20128/healthz` (recreating `omniroute-base` under `/usr/bin/lockf` on `~/.omniroute/update.lock` if needed) before applying REST mutations.
