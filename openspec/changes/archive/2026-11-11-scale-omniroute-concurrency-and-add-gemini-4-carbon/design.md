# Design

## Context

See `proposal.md - Why` for motivation. OmniRoute (`v3.8.53`, pinned digest in `/Users/androidteam/Omniroute/docker-compose.override.yml`) serves both `iosteam-mac-mini` (`127.0.0.1:20128` / `:20129` and Tailscale `100.70.16.83:20128` / `:20129`) and remote peer `macbook-pro-m5` (`100.106.143.78`). Because we track official `diegosouzapw/omniroute` releases via `~/Omniroute/scripts/check-upstream.sh` and `~/Omniroute/scripts/update.sh`, our primary architectural constraint is **zero tracked source code modifications** (`git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` MUST remain empty). Every change must live in persistent SQLite tables (`/app/data/storage.sqlite` on named volume `omniroute-data`), untracked `/Users/androidteam/Omniroute/.env`, untracked `/Users/androidteam/Omniroute/docker-compose.override.yml`, or workstation client configs.

## Goals / Non-Goals

**Goals:**
- Scale concurrent heavy-request capacity from `32` (`16` primary + `16` headroom) to **`64` active streams** (`32` primary + `32` headroom) and eliminate premature `HTTP 503 chat_admission_busy` shedding on parked queue bytes (`4 MB -> 64 MB`) and active in-flight bytes (`137.36 MB -> 256 MB`).
- Operationalize Google Gemini 4 Carbon (`gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, `gemini-4-carbon-low`) with full `1,048,576` input context and `262,144` max output tokens using persisted SQLite capability overrides (`model_capability_overrides` and `model_context_overrides`) rather than source edits to `MODEL_SPECS`.
- Eliminate multi-account thundering-herd concentration, Pro account `429` leaks in `gemini-4-argon*`, and Ultra quota bleed from `gemini-3.8-flash-high` by migrating homogeneous `agy` combos to `strategy: "quota-weighted"` and isolating Ultra vs. Pro account pools.
- Register the 4 `gemini-4-carbon*` combos across all 15 workstation coding agent and editor configurations with atomic `0600` backups and zero changes to startup default models.

**Non-Goals:**
- Editing any file tracked by Git in `/Users/androidteam/Omniroute` or adding new chunk patches to `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`.
- Enabling `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` or `COMBO_AUTO_PRUNE_STALE_STEPS`.
- Altering default model selections in any coding agent CLI or editor.

## Decisions

### Decision 1: Pure Configuration & SQLite Override Architecture for `gemini-4-carbon-*` (Zero Source Code Edits)

- **Fact / Evidence**:
  - Upstream Antigravity (`agy`) already syncs `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` (`outputTokenLimit: 262144`) into `syncedAvailableModels` (SQLite `key_value`) on the 3 Google AI Ultra accounts (`0532bad4`, `338764b8`, `62af823b`), while returning `gemini-4-carbon-disabled` on the 11 Google AI Pro accounts.
  - OmniRoute `v3.8.53` already supports `gemini-4-carbon-*` across all request-translation and quota layers without code changes:
    1. `open-sse/services/thinkingBudget.ts:69` (`/(?:^|[\/])gemini-(?:3\.8|4)(?:$|[-.])/i`) matches `gemini-4-carbon-*` and emits `thinkingLevel: "low" | "medium" | "high"`.
    2. `open-sse/services/antigravityQuotaFamily.ts:29` (`bare.startsWith("gemini-4")`) maps `gemini-4-carbon-*` to the `"argon"` weekly quota family (`quota_gemini-4-carbon-*` + `argon_weekly`).
    3. `src/lib/providerModels/syncedAutoAliases.ts:34` (`deriveSyncedTierAliases`) automatically derives `gemini-4-carbon -> agy/gemini-4-carbon-high` from synced discovery.
    4. `scripts/container-entrypoint-compat.sh:77` (`/^gemini-(?:[34](?:\.\d+)?(?:-[a-z0-9-]+)?|pro-agent)$/`) already strips trailing `role: "model"` turns on `gemini-4-carbon-*`.
  - The only gap in `v3.8.53` is that `src/shared/constants/modelSpecs.ts` (`MODEL_SPECS`) does not yet have a static `"gemini-4-carbon"` entry, so `getResolvedModelCapabilities("agy/gemini-4-carbon-*")` returns `contextWindow: null` and `maxOutputTokens: null` unless overridden in SQLite.
- **Decision**: Use 12 single-key `PATCH /api/model-capability-overrides` requests (`3 models × 4 keys`, passing `"low,medium,high"` as a comma-separated string for `reasoning_efforts`) to persist `context_length: 1048576` (in `model_context_overrides`), `max_input_tokens: 1048576`, `max_output_tokens: 262144`, and `reasoning_efforts: ["low", "medium", "high"]` (in `model_capability_overrides`) for `agy/gemini-4-carbon-high`, `agy/gemini-4-carbon-medium`, and `agy/gemini-4-carbon-low`. Setting `reasoning_efforts` is mandatory so `getComboTargetCatalogMetadata` (`src/app/api/v1/models/catalog.ts:692-703`) sets `source.reasoningEffortsOverride = true` and does not early-return before emitting `max_output_tokens: 262144`.
- **Tradeoff / Alternative**: Editing `src/shared/constants/modelSpecs.ts` would dirty the git checkout (breaking `update.sh` Gate P's `git merge --ff-only`) and would have zero effect on the pre-built Docker Hub container image unless rebuilt locally or patched via `container-entrypoint-compat.sh`. SQLite overrides are first-class in `src/lib/modelCapabilities.ts:846` (`getExplicitModelOutputCap` and `getResolvedModelCapabilities`) and survive all Docker image upgrades in the `omniroute-data` volume.

### Decision 2: Scaling Heavy Request Admission (`16 -> 32` Primary / `64` Total) & Eliminating the 4 MB Parked-Queue Bottleneck

```text
+-----------------------------------------------------------------------------------+
|                   CONCURRENT REQUEST PIPELINE (AFTER TUNING)                      |
+-----------------------------------------------------------------------------------+
|  Incoming Burst (up to 64+ parallel heavy MCP Router agent requests, 84+ tools)   |
|         |                                                                         |
|         v                                                                         |
|  [Layer 1: chatBodyAdmission.ts]                                                  |
|    * OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT = 32                                      |
|    * Healthy V8 Heap Headroom (<75% of 4096 MB): +32 extra slots = 64 ACTIVE      |
|    * OMNIROUTE_CHAT_MAX_INFLIGHT_BYTES = 268,435,456 (256 MB active bodies)       |
|    * Requests 65+: Park in fairness queue up to:                                  |
|        - OMNIROUTE_CHAT_ADMISSION_QUEUE_MS = 30,000 ms                            |
|        - OMNIROUTE_CHAT_ADMISSION_MAX_QUEUED_BYTES = 67,108,864 (64 MB parked)    |
|    * UV_THREADPOOL_SIZE = 32 (parallel zlib decompression & DNS lookup)           |
|         |                                                                         |
|         v                                                                         |
|  [Layer 2: quota-weighted Combo Router (quotaStrategies.ts:854-938)]              |
|    * Filters out exhausted/reserve accounts (remainingPercent > 5% on Ultra)     |
|    * Weights each account by:  weight = score / (1 + inflight)                    |
|    * Synchronously calls incrementInflight(winnerId) in same JS turn              |
|    * Releases inflight via quotaShareRelease when stream settles                  |
|         |                                                                         |
|         v                                                                         |
|  [Layer 3: Account Execution & Upstream Undici Pool]                              |
|    * ANTIGRAVITY_ACCOUNT_LEASE_ENABLED = "false" (no 503 POOL_BUSY on 3 Ultras)   |
|    * rate_limit_protection = 0 across all 14 active agy accounts                  |
|    * settings.requestQueue = { concurrentRequests: 64, requestsPerMinute: 600 }   |
|    * Undici HTTP/2 pool: 32 connections/origin, 60s keep-alive                    |
+-----------------------------------------------------------------------------------+
```

- **Fact / Evidence**:
  - In `src/shared/middleware/chatBodyAdmission.ts:395`, every request with `tools.length >= 64` or `content-length >= 256 KB` is classified as `"heavy"`. Because MCP Router attaches 84+ tools, 100% of coding-agent requests are `"heavy"`.
  - When active heavy requests exceed `maxHeavyInFlight + healthyHeadroom`, excess requests enter `acquireHeavyWithin(queueTimeoutMs)` (`chatBodyAdmission.ts:575`), which checks `queuedBytes + knownBytes > maxQueuedBytes`. The default `OMNIROUTE_CHAT_ADMISSION_MAX_QUEUED_BYTES` (`chatBodyAdmission.ts:114`) is only `4 * 1024 * 1024` (`4 MB`). Four queued ~1 MB coding-agent payloads fill the buffer, causing the 5th queued request to be shed immediately with `HTTP 503` (`reason: "queued_bytes_budget"`).
  - Similarly, `OMNIROUTE_CHAT_MAX_INFLIGHT_BYTES` auto-derives to `137.36 MB` (`admissionBudget.ts:50`), while the container's V8 heap is only using `514 MB` out of `4,096 MB` (`12.5%`).
- **Decision**: Configure both `/Users/androidteam/Omniroute/.env` and `/Users/androidteam/Omniroute/docker-compose.override.yml` (`environment:`) with:
  - `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=32` (32 primary + 32 healthy headroom = 64 immediate concurrent heavy streams)
  - `OMNIROUTE_CHAT_ADMISSION_MAX_QUEUED_BYTES=67108864` (`64 MB`)
  - `OMNIROUTE_CHAT_MAX_INFLIGHT_BYTES=268435456` (`256 MB`)
  - `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=30000` (`30s`)
  - `UV_THREADPOOL_SIZE=32`

### Decision 3: Switching Multi-Account Antigravity Combos from `auto` to `quota-weighted` & Isolating Ultra vs. Pro Pools

- **Fact / Evidence**:
  - In `open-sse/services/autoCombo/engine.ts:168`, `groupIntoTiers()` only places candidates into `tiers.top` if their composite score is within `SCORE_EPSILON = 0.0001` of the leader, and `scoreAutoTargets()` does not track active in-flight concurrency. Under simultaneous bursts, `ScoreTierRotator` sends all concurrent requests to a single account (`62af823b`, drained to 4.2% while `0532bad4` at 96.1% and `338764b8` at 96.2% sit idle). Furthermore, `strategy: "auto"` sets `appliesQuotaCutoffGate: false` (`strategyRegistry.ts`), allowing dispatch to the 7 Pro accounts in `gemini-4-argon*` that have `0.0%` Argon quota.
  - Conversely, `strategy: "quota-weighted"` (`open-sse/services/combo/quotaStrategies.ts:854-938` and `applyStrategyOrdering.ts:218-242`) is built into official OmniRoute `v3.8.53`:
    - It filters out `0%` exhausted accounts (`remainingPercent > floor`, default `1%`).
    - It divides each candidate's quota score by `1 + getInflight(connectionId)` (`getQuotaWeightedDrawWeight`, line 807).
    - It calls `incrementInflight(winnerId)` **synchronously in the same JS turn** (line 938) before yielding, preventing concurrent pipelines from colliding on the same account, and decrements via `quotaShareRelease` when the stream completes.
  - On Google AI Ultra accounts (`0532bad4`, `338764b8`, `62af823b`), `retrieveUserQuota` shares one `gemini_weekly` bucket across `gemini-4-carbon-*`, `gemini-4-argon-*`, and `gemini-3.8-flash-high`. Furthermore, in `open-sse/services/genericQuotaFetcher.ts:315, 419`, `convertUsageToQuotaInfo` only filters quota windows by family when `requestedFamily === "gemini" || requestedFamily === "claude"`, leaving `requestedFamily === "argon"` (`gemini-4-argon*` and `gemini-4-carbon*`) unscoped across all account windows (`max(percentUsed)`). If Claude 4.6 quota on an Ultra account were drained to `0%`, `convertUsageToQuotaInfo` would report `limitReached: true` (`0%` remaining) for `gemini-4-carbon*` and `gemini-4-argon*` on that Ultra account even when 96% of its Carbon/Argon quota remains.
- **Decision**:
  1. Create `gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` with `strategy: "quota-weighted"` (`quotaWeightedFloorPercent: 5`) across the 3 Ultra accounts (`0532bad4`, `338764b8`, `62af823b`).
  2. Update `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` to `strategy: "quota-weighted"` (`quotaWeightedFloorPercent: 5`) and prune the 7 Pro accounts so only the 3 Ultra accounts (`0532bad4`, `338764b8`, `62af823b`) remain.
  3. Update `gemini-3.8-flash-high` to `strategy: "quota-weighted"` (`quotaWeightedFloorPercent: 1`, `config.targetTimeoutMs: 120000`, raised from `25000` to prevent premature 25s aborts and `modelLockout` cascades on large-context `effort=high` agent turns) and pin its steps to the **11 active Pro accounts** (`38782750`, `9d66311f`, `ce95e1cb`, `9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`), removing all 3 Ultra accounts.
  4. Update `claude-opus-5.5` and `claude-sonnet-5.5` to `strategy: "quota-weighted"` (`quotaWeightedFloorPercent: 1`) across the **11 active Pro accounts** (9 Pro accounts on native `agy/claude-opus-5-5-high` / `agy/claude-sonnet-5-5-high` at 100% quota + 2 Pro accounts `9d66311f` and `ce95e1cb` on `agy/claude-opus-4-6-thinking` / `agy/claude-sonnet-4-6`), excluding the 3 Ultra accounts so Claude traffic never triggers `genericQuotaFetcher.ts`'s unscoped `argon` family aggregation.
  5. Set `predictiveTtftMs: 0` on all combos and in `/api/settings/combo-defaults` (required by `update.sh` Gate 8b `TTFT_ZERO` check and prevents false latency-cascade lockouts during long-context prefill).

### Decision 4: Transaction & Persistence Boundaries Across Container Recreation and Upstream Updates

- **SQLite (`omniroute-data` volume)**: All combo definitions (`combos`), capability overrides (`model_capability_overrides`, `model_context_overrides`), connection flags (`provider_connections.rate_limit_protection`), and settings (`key_value`) are mutated through authenticated HTTP API calls (`http://127.0.0.1:20128/api/*`) or bounded `better-sqlite3` transactions with `invalidateDbCache()`. Before any mutation, a verified SQLite snapshot is written to `~/.omniroute/snapshots/`.
- **Container Recreation**: Updating `.env` and `docker-compose.override.yml` requires holding `/usr/bin/lockf -s -t 60 /Users/androidteam/.omniroute/update.lock` around `docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base` and `~/Omniroute/scripts/ensure-muse-wire-compat.sh omniroute` (so `omniroute-watchdog.sh` does not race recreation), followed by Gate 8b verification (`MEM_OFF|CACHE_ALIGNED|COMP_OFF|TTFT_ZERO|PATCH_OK`).
- **Host Client Configs**: Every mutated host config file is backed up (`mode 0600`) with a SHA-256 manifest in `~/.omniroute/backups/scale-omniroute-concurrency-and-add-gemini-4-carbon/` before atomic temp-file replacement.

## Risks / Trade-offs

- **Risk: Ultra Account `62af823b` Has Only 3.7% Remaining Quota Until `2026-11-13T23:51:27Z`**
  - *Mitigation*: Under `strategy: "quota-weighted"` with `quotaWeightedFloorPercent: 5`, `62af823b` (`3.7%` model / `4.08%` weekly remaining) is below the `5%` floor and is completely protected from routine dispatch while `0532bad4` (`97.4%` model / `81.4%` weekly) and `338764b8` (`92.5%` model / `57.4%` weekly) handle traffic; if all 3 Ultra accounts ever drop below `5%`, `orderTargetsByQuotaWeighted` automatically fails open (`if (scored.length === 0) return expandedTargets`) so the `<5%` reserve remains usable.
- **Risk: `update.sh` Gate 8b Enforces `TTFT_ZERO` (`comboDefaults.predictiveTtftMs === 0`)**
  - *Mitigation*: Keep `comboDefaults.predictiveTtftMs: 0` in `/api/settings/combo-defaults` and `config.predictiveTtftMs: 0` on combos so `update.sh` Gate 8b (`MEM_OFF|CACHE_ALIGNED|COMP_OFF|TTFT_ZERO|PATCH_OK`) passes unconditionally while `targetTimeoutMs` (`180000` on Carbon/Argon/Opus, `120000` on Flash/Sonnet/Kimi/DeepSeek, `25000` on Muse) bounds individual stalled attempts. Raising `gemini-3.8-flash-high`'s `targetTimeoutMs` from `25,000 ms` to `120,000 ms` prevents premature 25s aborts and subsequent `modelLockout` cascades during large-context `effort=high` subagent turns.
- **Risk: Higher Memory Footprint at 64 Concurrent Heavy Requests (`256 MB` Inflight + `64 MB` Queued)**
  - *Mitigation*: Even at peak (`256 MB` active + `64 MB` queued × ~4× V8 parse overhead ≈ `1.28 GB`), total V8 heap (`~514 MB` baseline + `1.28 GB` = `~1.8 GB`) stays well below `NODE_OPTIONS=--max-old-space-size=4096` (`4 GB`) and the `75%` (`3.07 GB`) adaptive shed ratio.
