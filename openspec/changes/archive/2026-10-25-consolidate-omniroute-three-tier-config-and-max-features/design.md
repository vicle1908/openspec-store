# Design

## Context

See `proposal.md` — Why for motivation. In `/Users/androidteam/Omniroute/`, upstream `docker-compose.yml` (`x-common`, lines 36–73) declares `env_file: .env`, interpolates `${API_HOST:-127.0.0.1}`, and defines `omniroute-base` (`container_name: omniroute`), `redis` (`container_name: omniroute-redis`), and `qdrant` (`container_name: omniroute-qdrant`, `qdrant/qdrant:v1.12.4`, `127.0.0.1:6333:6333`, `127.0.0.1:6334:6334`, volume `qdrant-data:/qdrant/storage` with `name: omniroute-qdrant-data` under `profiles: [memory]`, lines 277–295, 427–428).

Four source-verified architectural realities govern this design:
1. **Docker Compose Merge Semantics vs. YAML Anchor Merge**: Inside a single Compose file, redeclaring `environment:` on a service that uses YAML anchor merge (`<<: *common`, `docker-compose.yml:L103`) replaces the anchor's `environment` sequence. Across multiple Compose files (`docker-compose.yml` + `docker-compose.override.yml`), however, `docker compose` merges `environment` entries by variable key rather than wiping unmentioned keys from `x-common.environment`. Even so, omitting `environment:` from `docker-compose.override.yml` and placing process variables in `.env` (`env_file: .env`) eliminates split-brain overrides and lets `/app/check-permissions.sh` append `--max-old-space-size=${OMNIROUTE_MEMORY_MB}` after `x-common`'s `--max-old-space-size=2048` (V8 honors the last flag).
2. **Workstation Memory Budget (`16 GiB` Host / `6 GiB` Docker VM), Cgroup Ceiling (`5g`) & Heavyweight Admission (`1`)**:
   - Upstream `docs/guides/DOCKER_GUIDE.md:L331` mandates: *"Size cgroup `--memory` above the heap — native buffers, SQLite, and compression intermediates sit outside V8."*
   - On this 16 GiB Mac Mini (`sysctl hw.memsize = 17,179,869,184` bytes), Docker Desktop is configured with `MemoryMiB: 6144` (`~/Library/Group Containers/group.com.docker/settings-store.json:L25`, `docker info` `MemTotal = 6,210,043,904` bytes / ~5.78 GiB). Today, `omniroute-base` has no `mem_limit`, so `process.constrainedMemory()` (`src/shared/middleware/admissionBudget.ts:86-94`) returns `18446744073709552000` (`2^64`).
   - Setting `OMNIROUTE_MEMORY_MB=4096` in `.env` (`heap_size_limit = 4,395,630,592` bytes / ~4.09 GiB) and `mem_limit: 5g` (`5,368,709,120` bytes) on `omniroute-base` in `docker-compose.override.yml` satisfies `V8 heap (4.09 GiB) < container cgroup (5.00 GiB) < LinuxKit VM (5.78 GiB)`—providing ~900 MiB of off-heap headroom for native buffers/SQLite WAL inside `omniroute` and ~800 MiB for `omniroute-qdrant` + `omniroute-redis`, while `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1` (`src/shared/middleware/chatBodyAdmission.ts:68-179,808`, where `countCapEnabled` is `maxHeavyInFlight < Number.MAX_SAFE_INTEGER`) serializes heavyweight (`> 256 KB`) coding-agent turns cleanly.
3. **Per-Subsystem Runtime Precedence (Not Universal `SQLite > .env`)**:
   - Different OmniRoute subsystems resolve configuration in different orders (`featureFlags.ts` and `qdrant.ts` are DB-first, whereas `semanticCacheConfig.ts` is env-first and `semanticCacheDbBridge.ts` is only registered on `/v1/chat/completions` and `/api/settings/cache-config`).
4. **Feature Flag Registration vs. Consumer Authority (`OMNIROUTE_MCP_COMPRESS_DESCRIPTIONS` & SearXNG)**:
   - Although `OMNIROUTE_MCP_COMPRESS_DESCRIPTIONS` is listed in `src/shared/constants/featureFlagDefinitions.ts:618`, `open-sse/mcp-server/server.ts:138-148` reads `key_value` (`namespace = 'compression'`, `key = 'mcpDescriptionCompressionEnabled'`) and `open-sse/mcp-server/descriptionCompressor.ts:50-56` only checks `process.env.OMNIROUTE_MCP_COMPRESS_DESCRIPTIONS` for disable values (`"0"`, `"false"`, `"off"`, `"no"`)—never `namespace = 'feature_flags'`. Thus MCP description compression MUST be enabled via `PUT /api/settings/compression` (`mcpDescriptionCompressionEnabled: true`), leaving 25 enabled `"true"` flags in `feature_flags`.
   - Removing `OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS=true` restores `"block-metadata"` SSRF guard mode on provider validation and embedding endpoints (`src/shared/network/outboundUrlGuardPolicy.ts:80-115`), blocking cloud metadata (`169.254.169.254`) while `OMNIROUTE_ALLOW_LOCAL_PROVIDER_URLS=true` (default) continues permitting Host Ollama (`http://host.docker.internal:11434/v1/embeddings`). Unconfigured default SearXNG (`http://localhost:8888/search`) on `/v1/search` is already excluded independently by `isUnconfiguredLoopbackSearchProvider()` (`open-sse/config/searchRegistry.ts:507-513`).

## Goals / Non-Goals

**Goals:**
- Consolidate OmniRoute configuration into three clean files (`storage.sqlite`, `~/Omniroute/.env`, and a structural `~/Omniroute/docker-compose.override.yml` with zero `environment:` overrides) respecting each subsystem's actual precedence contract.
- Enforce bounded memory and heavyweight admission for the 6 GiB Docker Desktop VM (`OMNIROUTE_MEMORY_MB=4096` in `.env`, `mem_limit: 5g` on `omniroute-base`, and `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1`).
- Persist all 25 verified `v3.8.52` coding-agent `feature_flags` as `"true"` and `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` as `"false"` in SQLite (`source: "db"`), persist `mcpDescriptionCompressionEnabled: true` via `PUT /api/settings/compression`, set `sessionAffinityTtlMs: 300000`, and verify all newly enabled behaviors safely with pre-deployment snapshots.

**Non-Goals:**
- Editing any git-tracked file in `/Users/androidteam/Omniroute/` or adding new runtime JS patches to `scripts/container-entrypoint-compat.sh`.
- Retiring Qdrant (`omniroute-qdrant`) or Redis (`omniroute-redis`) sidecars or removing the 12 existing fail-closed compatibility patches.

## Decisions

### 1. Per-Subsystem Precedence Authority & Three-Tier File Boundaries

| Subsystem | Code Authority | Runtime Precedence Order (Highest -> Lowest) | Required Operational Rule |
|---|---|---|---|
| **Feature Flags** (`25` `"true"` + `1` `"false"`) | `src/shared/utils/featureFlags.ts:13-22` | `SQLite key_value (namespace='feature_flags')` > `process.env` > `FEATURE_FLAG_DEFINITIONS.defaultValue` | Persist all 26 overrides via `PUT /api/settings/feature-flags` (`source: "db"`); remove duplicate flag vars from `docker-compose.override.yml` and `.env`. |
| **MCP Description Compression** | `open-sse/mcp-server/server.ts:138-148`, `descriptionCompressor.ts:50-56` | `process.env.OMNIROUTE_MCP_COMPRESS_DESCRIPTIONS` (disable-only: `0`/`false`/`off`/`no`) > `SQLite key_value (namespace='compression', key='mcpDescriptionCompressionEnabled')` > `true` | Persist `mcpDescriptionCompressionEnabled: true` via `PUT /api/settings/compression`; do not rely on `feature_flags` (ignored by MCP server) and do not set disable values in `.env`. |
| **Qdrant Hybrid Memory** | `src/lib/memory/qdrant.ts:59-145` | `SQLite key_value (namespace='settings', qdrant*)` > `process.env.QDRANT_*` > code defaults | Persist `enabled`, `host`, `port`, `collection`, `embeddingModel`, `quantization` via `PUT /api/settings/qdrant`; supply `QDRANT_VECTOR_SIZE=1024` & `QDRANT_HNSW_EF_CONSTRUCT=128` in `.env` (omitted by `.strict()` API schema). |
| **Layer-2 Semantic Cache** | `open-sse/config/semanticCacheConfig.ts:112-201`, `src/lib/cache/semanticCacheDbBridge.ts:46-83` | `process.env.OMNIROUTE_SEMANTIC_CACHE_*` > registered SQLite resolver (`database_settings.cache`) > `DEFAULT_SEMANTIC_CACHE_CONFIG` | Keep `OMNIROUTE_SEMANTIC_CACHE_*` in `.env` so `/v1/responses`-first and `/v1/messages`-first cold starts initialize `SemanticCacheManager` (including env-only `HISTORY_DEPTH=10`, `HISTORY_THRESHOLD=50`, `EXCLUDE_SYSTEM=true`), and keep overlapping fields in `PUT /api/settings/cache-config` identical because `.env` shadows dashboard/API edits. |
| **Process, Admission & Storage Caps** | `check-permissions.sh`, `chatBodyAdmission.ts`, `callLogs.ts`, `core.ts` | `process.env` (`.env` via `env_file: .env`) > code defaults | Define `API_HOST=0.0.0.0`, `OMNIROUTE_MEMORY_MB=4096`, `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1`, `CALL_LOG_*`, `CHAT_LOG_*`, `PROXY_LOGS_*`, `OMNIROUTE_SQLITE_SLOW_MS=200`, `OMNIROUTE_SKIP_DB_HEALTHCHECK=1`, `OMNIROUTE_MAX_TOOLS_LIMIT=256`, `MEMORY_VEC_QUANTIZATION=int8`, `MEMORY_RRF_K=60`, and `OMNIROUTE_DEFAULT_OWNER_ID` in `.env`. |
| **Structural Compose Overlay** | `docker-compose.yml` + `docker-compose.override.yml` | Compose file structural merge | Restrict `docker-compose.override.yml` to image, `mem_limit`, `extra_hosts`, volumes/entrypoint mount, healthcheck (`timeout: 15s`, `start_period: 120s`), `redis` `ports: !reset []`, and `qdrant` `profiles: !override [base, memory]` + `/dev/tcp` healthcheck with **zero `environment:` entries**, preserving upstream container identities (`omniroute`, `omniroute-redis`, `omniroute-qdrant`). |

### 2. Bounded V8 Heap (`4096` MB), Container Cgroup Cap (`5g`) & Heavyweight Admission (`1`)
- **Decision**: Set `OMNIROUTE_MEMORY_MB=4096` and `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1` in `.env`, and set `mem_limit: 5g` on `omniroute-base` in `docker-compose.override.yml`.
- **Rationale**: On the 16 GiB Mac Mini (`MemoryMiB: 6144` in Docker Desktop, `MemTotal = 6,210,043,904` bytes), `OMNIROUTE_MEMORY_MB=4096` + `mem_limit: 5g` keeps V8 old-space (`4,395,630,592` bytes) strictly below the container cgroup limit (`5,368,709,120` bytes), which in turn sits below total LinuxKit VM RAM (`6,210,043,904` bytes). Setting `mem_limit: 5g` also makes `process.constrainedMemory()` (`admissionBudget.ts:86-94`) return `5,368,709,120` instead of `2^64`, while `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1` sets `maxHeavyInFlight = 1` (`chatAdmission.countCapEnabled === true`, `chatAdmission.budgetSource: "v8_heap"`, `chatAdmission.maxInflightBytes: 137363456`).

### 3. Authoritative 25-Flag SQLite Inventory, Official MCP Description Compression & Behavioral Gates
- **Decision**: Persist the following **25** `v3.8.52` feature flags as `"true"` (plus `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED="false"`) in SQLite `key_value` (`namespace = 'feature_flags'`) via `PUT /api/settings/feature-flags`:
  1. `QUOTA_WINDOW_BOUNDED_PARK` — caps quota cooldowns to reset window (<=15m).
  2. `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED` — retries once on sibling connection on pre-first-frame SSE EOF.
  3. `COOLDOWN_RETRY_SKIP_REFUSALS_ENABLED` — skips cooldown retries on terminal 4xx refusals.
  4. `PROVIDER_SAFETY_STOPS_TERMINAL` — treats safety/content-policy blocks as terminal.
  5. `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED` — fails over once when stream closes with zero output tokens.
  6. `STREAM_READINESS_STALL_RETRY` — retries stalled pre-first-chunk streams.
  7. `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED` — defers expensive SQLite integrity checks off startup path.
  8. `STREAM_LATE_OUTPUT_PROBE_ENABLED` — probes late output before aborting stream.
  9. `RETRY_AFTER_PROVENANCE_ENABLED` — honors upstream `Retry-After` provenance.
  10. `COMBO_EMPTY_POOL_NO_ELIGIBLE_TARGETS_ENABLED` — returns explicit empty-pool diagnostics when all targets are filtered.
  11. `CREDENTIAL_GATE_AUTH_DIAGNOSES_ONLY` — restricts credential gate to auth diagnostics without false lockouts.
  12. `AUTO_REQUEST_RESOLVED_CAPABILITIES` — feeds resolved capabilities (vision, reasoning, thinking) into `auto/*` scoring.
  13. `AUTO_COMBO_KEYLESS_TRANSPORT_GATE` — excludes keyless `browserBacked`/`isLocalCli` providers from `auto/*` pools.
  14. `MODELS_DEV_EFFORT_TIERS_ENABLED` — populates `effort_tiers` (`low`, `medium`, `high`, `xhigh`) on `/v1/models` and combo intersections.
  15. `CATALOG_MIRROR_REFINEMENTS_ENABLED` — refines `/v1/models` mirror passes for reasoning variants and active gateways.
  16. `ANTHROPIC_COMPATIBLE_MID_CONVERSATION_SYSTEM` — preserves mid-conversation `role: "system"` turns on `anthropic-compatible-*` relays when `mid-conversation-system-2026-04-07` beta is present.
  17. `CONTENT_POLICY_REFUSAL_COMBO_STOP_ENABLED` — stops heterogeneous combos immediately on explicit content/cyber policy refusal.
  18. `CREDENTIAL_HEALTH_RETEST_AUTO_DISABLED` — periodically retests `autoDisabledAt` connections (max 1 per 6h) without touching operator-disabled or banned accounts.
  19. `MODEL_ENDPOINT_CAPABILITY_GATE_ENABLED` — blocks unsupported model/endpoint dispatches with HTTP 400 and filters `/v1/models`.
  20. `OPENCODE_FULL_TEXT_ERROR_RULES_ENABLED` — inspects full OpenCode Zen/Go error bodies for quota lockout classification.
  21. `CLOUDFLARE_AI_FULL_TEXT_ERROR_RULES_ENABLED` — inspects Cloudflare Workers AI error bodies for daily allocation exhaustion.
  22. `PROTECTED_PRIORITY_INFRA_502_ENABLED` — returns HTTP 502 instead of HTTP 503 when protected priority targets fail on verified infra faults (`circuit_open`, TTFT timeout).
  23. `COMBO_AUTO_PRUNE_STALE_STEPS` — removes explicit combo steps delisted during authoritative live catalog syncs (`src/lib/combos/staleModelPrune.ts`), never pruning on failed/degraded/free-only syncs and never emptying a combo.
  24. `NATIVE_CODEX_REACTIVE_COMPACTION_ENABLED` — reactively compacts oversized native Codex passthrough histories (`POST /v1/responses`).
  25. `CLAUDE_OAUTH_SUMMARIZED_THINKING_UNREDACTED` — drops `redact-thinking-2026-02-12` when `thinking.display: "summarized"` is requested.
- **Companion Settings & Safeguards**:
  - Persist `mcpDescriptionCompressionEnabled: true` via `PUT /api/settings/compression`.
  - Persist `sessionAffinityTtlMs: 300000` via `PATCH /api/settings` and verify multi-turn connection pinning, cross-session isolation, and failover when the pinned connection fails.
  - Snapshot combos (`GET /api/combos`) and SQLite (`PUT /api/db-backups`) before enabling `COMBO_AUTO_PRUNE_STALE_STEPS`, and verify both authoritative-sync pruning and degraded-sync preservation.

## Risks / Trade-offs

- **Risk**: `resolveSemanticCacheConfig()` (`open-sse/config/semanticCacheConfig.ts:120-201`) checks `process.env.OMNIROUTE_SEMANTIC_CACHE_*` before `dynamic` (`database_settings.cache`), and `ensureSemanticCacheDbBridge()` is not invoked on `/v1/responses` or `/v1/messages` cold starts.
  - **Mitigation**: Keep `OMNIROUTE_SEMANTIC_CACHE_*` in `.env` for cold-start `/v1/responses` and `/v1/messages` parity without adding new JS patches, and require any change to overlapping semantic-cache settings to be applied to both `.env` and `PUT /api/settings/cache-config`.
- **Risk**: Without a container `mem_limit`, `process.constrainedMemory()` returns `2^64` on Docker Desktop and off-heap buffers can contend with `omniroute-qdrant` and `omniroute-redis` inside the 5.78 GiB LinuxKit VM.
  - **Mitigation**: Set `mem_limit: 5g` on `omniroute-base` above `OMNIROUTE_MEMORY_MB=4096` and set `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1`.
- **Risk**: `COMBO_AUTO_PRUNE_STALE_STEPS="true"` mutates stored combo definitions after authoritative catalog syncs.
  - **Mitigation**: Capture a pre-change `GET /api/combos` JSON export and `PUT /api/db-backups` SQLite snapshot before activation, verify all active workstation combos remain intact after sync, and test degraded/failed sync non-mutation.
