# Spec Delta

## MODIFIED Requirements

### Requirement: Bounded Quota Park, Early-EOF Sibling Failover, Refusal Cooldown Skip, and Terminal Safety Stops

OmniRoute SHALL persist all 25 enabled v3.8.52 resilience, routing, catalog, and compaction feature flags as "true" and ANTIGRAVITY_ACCOUNT_LEASE_ENABLED as "false" in SQLite feature_flags, configure mcpDescriptionCompressionEnabled as true in compression settings, set sessionAffinityTtlMs to 300000, and keep FLUSH_EMPTY_RETRY_ENABLED and OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS disabled ("false") while OMNIROUTE_ALLOW_LOCAL_PROVIDER_URLS remains "true".

#### Scenario: Pre-first-frame SSE early EOF fails over once to a sibling connection
- **WHEN** `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED` is `true` and an upstream SSE stream closes with `STREAM_EARLY_EOF` before emitting any useful frame
- **THEN** OmniRoute SHALL exclude the failed connection and retry once on an eligible sibling connection

#### Scenario: Content-policy safety refusal stops combo retry loop
- **WHEN** `PROVIDER_SAFETY_STOPS_TERMINAL` and `CONTENT_POLICY_REFUSAL_COMBO_STOP_ENABLED` are `true` and an upstream target returns HTTP 400 or 403 with `content_policy_violation`, `cyber_policy`, or `misalignment_policy_violation`
- **THEN** OmniRoute SHALL treat the refusal as terminal for the request and SHALL NOT retry the refused prompt across remaining combo targets

#### Scenario: Expanded v3.8.52 coding-agent feature flags and MCP description compression resolve from authoritative SQLite tables
- **WHEN** `GET /api/settings/feature-flags` and `GET /api/settings/compression` are queried with management authentication
- **THEN** all 25 enabled flags (`QUOTA_WINDOW_BOUNDED_PARK`, `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED`, `COOLDOWN_RETRY_SKIP_REFUSALS_ENABLED`, `PROVIDER_SAFETY_STOPS_TERMINAL`, `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED`, `STREAM_READINESS_STALL_RETRY`, `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED`, `STREAM_LATE_OUTPUT_PROBE_ENABLED`, `RETRY_AFTER_PROVENANCE_ENABLED`, `COMBO_EMPTY_POOL_NO_ELIGIBLE_TARGETS_ENABLED`, `CREDENTIAL_GATE_AUTH_DIAGNOSES_ONLY`, `AUTO_REQUEST_RESOLVED_CAPABILITIES`, `AUTO_COMBO_KEYLESS_TRANSPORT_GATE`, `MODELS_DEV_EFFORT_TIERS_ENABLED`, `CATALOG_MIRROR_REFINEMENTS_ENABLED`, `ANTHROPIC_COMPATIBLE_MID_CONVERSATION_SYSTEM`, `CONTENT_POLICY_REFUSAL_COMBO_STOP_ENABLED`, `CREDENTIAL_HEALTH_RETEST_AUTO_DISABLED`, `MODEL_ENDPOINT_CAPABILITY_GATE_ENABLED`, `OPENCODE_FULL_TEXT_ERROR_RULES_ENABLED`, `CLOUDFLARE_AI_FULL_TEXT_ERROR_RULES_ENABLED`, `PROTECTED_PRIORITY_INFRA_502_ENABLED`, `COMBO_AUTO_PRUNE_STALE_STEPS`, `NATIVE_CODEX_REACTIVE_COMPACTION_ENABLED`, `CLAUDE_OAUTH_SUMMARIZED_THINKING_UNREDACTED`) SHALL report `effectiveValue: "true"` and `source: "db"`, `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` SHALL report `effectiveValue: "false"` and `source: "db"`, and `GET /api/settings/compression` SHALL report `mcpDescriptionCompressionEnabled: true`

#### Scenario: Outbound provider URL guard blocks cloud metadata while permitting Host Ollama
- **WHEN** `OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS` is `"false"` and `OMNIROUTE_ALLOW_LOCAL_PROVIDER_URLS` is `"true"`
- **THEN** `getProviderOutboundGuard()`, `getProviderValidationGuard()`, and `embeddingUrlGuard()` SHALL operate in `"block-metadata"` mode—rejecting cloud metadata endpoints (`169.254.169.254`, `fd00:ec2::254`, `metadata.google.internal`) before any network request is dispatched while permitting Host Ollama (`http://host.docker.internal:11434/v1/embeddings`)—and `/v1/search` SHALL independently skip unconfigured default SearXNG (`http://localhost:8888/search`) via `isUnconfiguredLoopbackSearchProvider`

#### Scenario: Stale combo step auto-prune snapshots combos and prunes only on authoritative catalog syncs
- **WHEN** `COMBO_AUTO_PRUNE_STALE_STEPS` is `"true"` after a pre-deployment combo and SQLite backup snapshot has been recorded
- **THEN** OmniRoute SHALL remove explicit combo model steps only when an authoritative live catalog sync confirms the model is delisted, SHALL NOT prune steps on failed, degraded, or free-only syncs, and SHALL NEVER empty a combo whose every step is flagged stale

#### Scenario: Session affinity pins multi-turn connections with cross-session isolation and unhealthy failover
- **WHEN** `sessionAffinityTtlMs` is configured to `300000` (5 minutes)
- **THEN** subsequent turns within the same session window SHALL prefer the pinned connection, distinct session IDs SHALL route independently without sharing affinity pins, and OmniRoute SHALL immediately fail over to a healthy sibling connection if the pinned connection errors or enters cooldown

### Requirement: Bounded SQLite Table Retention, Usage Rollup Aggregation, and Call-Log Artifact Caps

OmniRoute SHALL configure bounded database retention (`conversationTurnNodes: 2`, `usageHistory: 30`, `quotaSnapshots: 3`, `callLogs: 7`, `compressionAnalytics: 7`, `compressionCacheStats: 7`, `xpAuditLog: 7`, `domainCostHistory: 14`), enable `aggregation` (`enabled: true`), limit daily DB backups (`keepLastNBackups: 2`), and cap call-log and proxy-log storage (`CALL_LOG_MAX_ENTRIES=2000`, `CHAT_LOG_MAX_BODY_KB=256`, `CALL_LOGS_TABLE_MAX_ROWS=25000`, `PROXY_LOGS_TABLE_MAX_ROWS=25000`).

#### Scenario: Usage history rollup and bounded table retention on auto-cleanup
- **WHEN** the 6-hourly `runAutoCleanup()` pass executes with `aggregation.enabled: true` and `retention.usageHistory: 30`
- **THEN** OmniRoute SHALL roll up `usage_history` rows older than 30 days into `daily_usage_summary` before deleting them, prune `conversation_turn_nodes` older than 2 days and `quota_snapshots` older than 3 days, and reclaim freed SQLite pages via bounded `PRAGMA incremental_vacuum`

#### Scenario: Call-log artifact volume bounded on disk
- **WHEN** `CALL_LOG_MAX_ENTRIES=2000`, `CHAT_LOG_MAX_BODY_KB=256`, `CALL_LOGS_TABLE_MAX_ROWS=25000`, and `PROXY_LOGS_TABLE_MAX_ROWS=25000` are configured in `/Users/androidteam/Omniroute/.env`
- **THEN** `rotateCallLogs()` and SQLite log pruning SHALL cap `/app/data/call_logs/` at 2,000 JSON files with bodies truncated at 256 KB and cap `call_logs` and `proxy_logs` tables at 25,000 rows

## ADDED Requirements

### Requirement: Three-Tier Configuration Hierarchy and Coding-Agent V8 Heap Sizing

OmniRoute SHALL separate configuration across SQLite runtime tables, ~/Omniroute/.env, and a structural ~/Omniroute/docker-compose.override.yml with zero environment overrides, aligning overlapping semantic-cache keys across .env and SQLite and sizing omniroute-base with OMNIROUTE_MEMORY_MB=4096, container mem_limit: 5g, and single-heavyweight admission (OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1) within the 6 GiB Docker Desktop VM.

#### Scenario: Bounded V8 heap, 5 GiB container cgroup limit, and single-heavyweight admission within the 6 GiB Docker VM
- **WHEN** `omniroute-base` starts with `OMNIROUTE_MEMORY_MB=4096` and `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1` in `.env` and `mem_limit: 5g` in `docker-compose.override.yml` on the `6144` MiB (`MemTotal = 6,210,043,904` bytes) Docker Desktop VM
- **THEN** `/app/check-permissions.sh` SHALL configure `v8.getHeapStatistics().heap_size_limit` (`4,395,630,592` bytes) strictly below `process.constrainedMemory()` (`5,368,709,120` bytes / `5g`), which in turn SHALL remain below Docker VM `MemTotal` (`6,210,043,904` bytes), and `GET /api/monitoring/health` SHALL report `chatAdmission.countCapEnabled: true`, `chatAdmission.budgetSource: "v8_heap"`, and `chatAdmission.maxInflightBytes: 137363456`

#### Scenario: Structural docker-compose.override.yml preserves service identities, healthcheck timing, and zero environment overrides
- **WHEN** `/Users/androidteam/Omniroute/docker-compose.override.yml` and `docker compose --profile base config` are inspected
- **THEN** `docker-compose.override.yml` SHALL contain zero `environment:` entries and only structural service overrides (Hub image `diegosouzapw/omniroute:latest`, explicit `mem_limit`, `extra_hosts` for `host.docker.internal`, named volume `omniroute-data:/app/data` and `container-entrypoint-compat.sh` mount, healthcheck `timeout: 15s` and `start_period: 120s`, `redis` `ports: !reset []`, and `qdrant` `profiles: !override [base, memory]` + `/dev/tcp` healthcheck) while preserving container identities `omniroute`, `omniroute-redis`, and `omniroute-qdrant`

#### Scenario: Cold-start Responses and Messages requests initialize semantic cache without management warmup and isolate tool contracts
- **WHEN** `omniroute` starts fresh and serves cold-start `POST /v1/responses` or `POST /v1/messages` requests before `/api/settings/cache-config` or `/v1/chat/completions` has been called
- **THEN** `SemanticCacheManager` SHALL initialize from the synchronized `OMNIROUTE_SEMANTIC_CACHE_*` variables in `.env` (returning `X-OmniRoute-Cache: HIT` on a repeated `temperature: 0` request with identical output and tool contracts) and SHALL return `X-OmniRoute-Cache: MISS` when `tools`, `tool_choice`, `response_format`, or tool-history digests differ
