# omniroute-compression-and-routing Specification

## Purpose

Defines the operational behavior, token compression rules, combo routing resilience invariants, thinking-budget passthrough policy, and feature-flag baseline for the OmniRoute AI gateway (`v3.8.52`) when serving multi-turn coding agents over loopback interfaces.

## Requirements

### Requirement: RTK Tool Result Compression, Adaptive Context Budget, and Delegated Context Editing

The OmniRoute gateway SHALL configure RTK compression at `minimal` intensity for tool result payloads while preserving system prompts and code blocks, SHALL configure `contextBudget.mode` as `"replace-autotrigger"` (`pct: 0.85`), and SHALL enable delegated `contextEditing` for supported Claude relays.

#### Scenario: Verbose tool output compressed before upstream dispatch
- **WHEN** a coding client submits a request carrying `x-omniroute-compression: allow-lossy` or `engine:rtk` (or tests via `POST /api/context/rtk/test` with an explicit `command`) containing a tool result matching one of the 55 built-in RTK filters
- **THEN** OmniRoute SHALL compress the tool result payload within `maxLinesPerResult` (120) and `maxCharsPerResult` (12000) bounds while preserving system prompts (`preserveSystemPrompt: true`) and code blocks (`applyToCodeBlocks: false`) verbatim

#### Scenario: Headerless requests honor safe default pipeline and adaptive context budget escalation
- **WHEN** a client submits a request without an `x-omniroute-compression` header
- **THEN** OmniRoute's `lossyRequestPolicy` SHALL run `SAFE_DEFAULT_PIPELINE` (`session-dedup` and `lite`) when below the 85% `contextBudget` threshold, and `resolveAdaptivePlan` SHALL escalate along the compression ladder (`session-dedup` -> `rtk` -> `headroom` -> `lite` -> `caveman`) when estimated input tokens exceed the `contextBudget` target

#### Scenario: Delegated context editing on long Claude tool loops
- **WHEN** `contextEditing.enabled` is `true` and a request targets a supported Claude or `anthropic-compatible-cc-*` relay exceeding the 100,000 input token trigger
- **THEN** OmniRoute SHALL inject the `clear_tool_uses_20250919` context management edit keeping the 3 most recent tool uses, and automatically strip and retry once if upstream returns HTTP 400

### Requirement: Dual Quota-Cache Keys on Auto-Routed Combos

All OmniRoute combos configured with `strategy: "auto"` or `candidatePool: ["agy"]` SHALL define both `resetAwareQuotaCache*` and `resetWindowQuotaCache*` TTL/max-stale keys (`300000` ms TTL, `3600000` ms max-stale) while preserving existing `config` fields.

#### Scenario: Subsequent auto-combo turn within 5-minute TTL window
- **WHEN** an inference request targets an `auto` combo (`gemini-3.8-flash-high`, `gemini-4-argon`, `gemini-4-argon-{high,medium,low}`, or `claude-opus-5.5`) whose upstream quota snapshot was refreshed less than 300,000 milliseconds ago
- **THEN** OmniRoute SHALL score candidates using the cached quota snapshot via `resetWindowQuotaCacheTtlMs` without blocking on a synchronous upstream `retrieveUserQuota` HTTP call

#### Scenario: Stale quota fallback on upstream telemetry timeout
- **WHEN** the 300,000 millisecond TTL has expired and an upstream quota refresh fails or times out within the 3,600,000 millisecond max-stale window
- **THEN** OmniRoute SHALL serve the last known quota snapshot while refreshing asynchronously in the background

### Requirement: Subset-Account Stickiness, Nested Combo Execution, and Active Target Hygiene

OmniRoute combos targeting Antigravity (`agy`) connection subsets SHALL set `context_cache_protection: false`, `muse-spark-1.3` SHALL set `strategy: "priority"` and `config.nestedComboMode: "execute"`, `claude-opus-5.5` SHALL set `strategy: "auto"` and `config.nestedComboMode: "flatten"`, and combos SHALL NOT retain targets whose provider has zero active connections.

#### Scenario: Multi-turn conversation on subset-account combo
- **WHEN** a client executes Turn 2 or later against `gemini-3.8-flash-high`, `gemini-4-argon*`, `muse-spark-1.3`, or `claude-opus-5.5`
- **THEN** OmniRoute SHALL route the request using connection-level session stickiness (`applySessionStickiness`) without logging false `provider durably unhealthy — dropping pin` warnings or escaping the combo's configured connections

#### Scenario: Nested combo-ref execution on `muse-spark-1.3` and auto-scored pool on `claude-opus-5.5`
- **WHEN** `muse-spark-1.3` dispatches to its primary `combo-ref` target (`gemini-3.8-flash-high`)
- **THEN** OmniRoute SHALL execute `gemini-3.8-flash-high` as an encapsulated runtime unit (`nestedComboMode: "execute"`) using its `auto` strategy before falling back to `agy/gemini-3.8-flash-medium`, while `claude-opus-5.5` (`strategy: "auto"`, `nestedComboMode: "flatten"`) SHALL score all 8 Opus accounts via 16-factor `auto` routing and `applySessionStickiness`

### Requirement: Thinking Budget Passthrough and Resilience Feature Flags

OmniRoute SHALL configure `thinkingBudget.mode` as `"passthrough"` and SHALL enable the v3.8.52 resilience feature flags `CREDENTIAL_GATE_AUTH_DIAGNOSES_ONLY`, `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED`, `COMBO_EMPTY_POOL_NO_ELIGIBLE_TARGETS_ENABLED`, `STREAM_LATE_OUTPUT_PROBE_ENABLED`, and `RETRY_AFTER_PROVENANCE_ENABLED` via individual string-valued (`"true"`) flag overrides.

#### Scenario: Client reasoning parameters preserved under passthrough mode
- **WHEN** Codex CLI, Claude Code, or OMP sends a request containing `reasoning`, `reasoning_effort`, `thinking`, or `thinking_config`
- **THEN** OmniRoute SHALL preserve those fields verbatim without stripping or overwriting them

#### Scenario: Antigravity concurrent account lease protection
- **WHEN** `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` is `true` and an in-flight streaming request is active on a specific `(connectionId, model)` pair
- **THEN** OmniRoute SHALL lease that `(connectionId, model)` pair for the duration of the stream so concurrent requests select an unleased sibling account

### Requirement: Built-in Memory and Skills Injection Disabled in Favor of Dedicated AgentMemory

OmniRoute SHALL configure `memoryEnabled: true`, `skillsEnabled: false`, and `memoryMaxTokens: 2000` via `/api/settings/memory`, keeping built-in skills and `memory_*` tool injection disabled when `skillsEnabled` is `false` while enabling always-on hybrid memory (`strategy: "hybrid"`, `vectorStore: "qdrant"`, `retentionDays: 60`) with shared workspace keyless owner fallback (`OMNIROUTE_DEFAULT_OWNER_ID` / `"6a72d8ab-88db-4d49-973b-864c6cbdace5"`) and `x-omniroute-no-memory: true` header opt-out.

#### Scenario: Authenticated chat request bypasses built-in memory injection and extraction
- **WHEN** an authenticated or keyless client submits a request carrying `x-omniroute-no-memory: true` to `/v1/chat/completions`, `/v1/messages`, or `/v1/responses`
- **THEN** OmniRoute SHALL set `memoryOwnerId = null` and SHALL neither prepend `Memory context:` nor inject `memory_*` tools nor run post-response regex fact extraction into the `memories` table, while always keeping `skillsEnabled: false` across all requests

#### Scenario: Internal memory store remains empty
- **WHEN** `GET /api/memory?limit=1` is queried before any non-opted-out conversation facts or explicit `POST /api/memory` entries are recorded (or after memory cleanup)
- **THEN** OmniRoute SHALL return `total: 0` and `stats.tokensUsed: 0`, and once entries are stored SHALL scope them by `apiKeyInfo.id` or `OMNIROUTE_DEFAULT_OWNER_ID` (`"6a72d8ab-88db-4d49-973b-864c6cbdace5"`) for keyless traffic without injecting `memory_*` tools into `body.tools` when `skillsEnabled` is `false`

### Requirement: Lossless `lite` Tool Result Preservation, `codex-responses` Engine, and Prose-Safe Context Budget Ladder

OmniRoute SHALL configure `lite.compressToolResults` as `false` (`maxToolLength: 200000`), SHALL enable `headroom` (`engines.headroom.enabled: true`) and `codex-responses` (`codexResponsesConfig.enabled: true`), and SHALL set `contextBudget` (`mode: "replace-autotrigger"`, `policy: "percentage"`, `pct: 0.85`) with `ladderOverride` ordered as `session-dedup`, `headroom`, `lite`, `codex-responses`, and `rtk` (`minimal`).

#### Scenario: Headerless multi-turn requests preserve prior-turn `Read` and `Grep` tool results under `[session-dedup, lite, headroom]`
- **WHEN** a coding client submits a multi-turn request without an `x-omniroute-compression` header and with prior-turn tool results exceeding 2,000 characters
- **THEN** OmniRoute SHALL run its lossless `[session-dedup, lite, headroom]` pipeline and `lite` SHALL NOT truncate prior-turn tool results to 2,000 characters (`compressToolResults: false`)

#### Scenario: Lossy-opt-in and `codex-responses` requests compress `/v1/responses` and `/v1/chat/completions` tool outputs while protecting file reads
- **WHEN** a request opts into lossy compression (`x-omniroute-compression: allow-lossy`, `engine:codex-responses`, or `engine:rtk`) or invokes `ladderOverride` (`basePlan.mode === "off"` at >85% `percentage` context budget)
- **THEN** OmniRoute SHALL execute `codex-responses` (on `/v1/responses` `function_call_output` items, protecting `Read`, `Glob`, `Grep`, `Write`, `Edit`, `WebSearch`, `WebFetch`, `find`) and `rtk` (`minimal` intensity on tool results)

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

### Requirement: Claude Classifier Short-Circuit, Fast Mode Opus 5.5 Support, 50 MB Body Limit, and `models.dev` Capability Sync

OmniRoute SHALL configure `claudeClassifierCompat: "auto"`, include `"claude-opus-5-5"` in `claudeFastMode.supportedModels`, set `maxBodySizeMb: 50`, and enable periodic `models.dev` capability sync (`modelsDevSyncEnabled: true`, `action: "start"`).

#### Scenario: Claude Code auto-mode security classifier short-circuited locally
- **WHEN** `claudeClassifierCompat` is `"auto"` and Claude Code sends an Anthropic Messages request whose system prompt contains `"You are a security monitor for autonomous AI coding agents"`
- **THEN** OmniRoute SHALL immediately return a synthetic HTTP 200 default-allow response (`<block>no</block>` or `<severity>0</severity>`) without dispatching an upstream LLM request

### Requirement: Bounded SQLite Table Retention, Usage Rollup Aggregation, and Call-Log Artifact Caps

OmniRoute SHALL configure bounded database retention (`conversationTurnNodes: 2`, `usageHistory: 30`, `quotaSnapshots: 3`, `callLogs: 7`, `compressionAnalytics: 7`, `compressionCacheStats: 7`, `xpAuditLog: 7`, `domainCostHistory: 14`), enable `aggregation` (`enabled: true`), limit daily DB backups (`keepLastNBackups: 2`), and cap call-log and proxy-log storage (`CALL_LOG_MAX_ENTRIES=2000`, `CHAT_LOG_MAX_BODY_KB=256`, `CALL_LOGS_TABLE_MAX_ROWS=25000`, `PROXY_LOGS_TABLE_MAX_ROWS=25000`).

#### Scenario: Usage history rollup and bounded table retention on auto-cleanup
- **WHEN** the 6-hourly `runAutoCleanup()` pass executes with `aggregation.enabled: true` and `retention.usageHistory: 30`
- **THEN** OmniRoute SHALL roll up `usage_history` rows older than 30 days into `daily_usage_summary` before deleting them, prune `conversation_turn_nodes` older than 2 days and `quota_snapshots` older than 3 days, and reclaim freed SQLite pages via bounded `PRAGMA incremental_vacuum`

#### Scenario: Call-log artifact volume bounded on disk
- **WHEN** `CALL_LOG_MAX_ENTRIES=2000`, `CHAT_LOG_MAX_BODY_KB=256`, `CALL_LOGS_TABLE_MAX_ROWS=25000`, and `PROXY_LOGS_TABLE_MAX_ROWS=25000` are configured in `/Users/androidteam/Omniroute/.env`
- **THEN** `rotateCallLogs()` and SQLite log pruning SHALL cap `/app/data/call_logs/` at 2,000 JSON files with bodies truncated at 256 KB and cap `call_logs` and `proxy_logs` tables at 25,000 rows

### Requirement: Server-Side Tool-Safe Default Compression Stack Without Prose Modification

OmniRoute SHALL disable `caveman` (`engines.caveman.enabled: false`, `cavemanConfig.enabled: false`) and SHALL configure `compressionComboId: "default-caveman"` with `stackedPipeline` ordered as `session-dedup`, `lite` (`compressToolResults: false`), `rtk` (`intensity: "minimal"`), `codex-responses`, and `headroom` so headerless coding requests execute tool-output compression automatically without modifying user or assistant prose.

#### Scenario: Headerless coding request executes `rtk` and `codex-responses` without prose mutation
- **WHEN** a coding client submits a multi-turn request without an `x-omniroute-compression` header containing verbose shell/test tool outputs and `Read`/`Grep` file outputs
- **THEN** OmniRoute (`config.compressionComboId === "default-caveman"`) SHALL execute `[session-dedup, lite, rtk, codex-responses, headroom]` to compress the shell/test tool outputs while preserving user/assistant prose (`caveman: false`) and `Read`/`Grep`/`Glob`/`Edit`/`Write` file outputs verbatim

### Requirement: Predictive TTFT Circuit Breaker, Unleased 2-Account Pool Concurrency, and Subscription-Scoped Ban Auto-Disable

OmniRoute SHALL enable `zeroLatencyOptimizationsEnabled: true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) in `/api/settings/combo-defaults` and `agy` combos (`gemini-3.8-flash-high`, `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, `claude-opus-5.5`, `muse-spark-1.3`), set `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` to `"false"`, and configure `/api/settings/auto-disable-accounts` (`enabled: true`, `scope: "subscription"`, `threshold: 3`).

#### Scenario: Stalled target exceeding 25-second average latency skipped on attempt 0 without fallback re-truncation
- **WHEN** `zeroLatencyOptimizationsEnabled` is `true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) and a target's historical `avgLatencyMs` in `getComboMetrics` exceeds 25,000 milliseconds
- **THEN** OmniRoute SHALL skip that target on primary attempt `0` (`predictive_ttft`) and dispatch to the next healthy candidate without issuing duplicate speculative hedged requests or running unconfigured fallback `lite` truncation

#### Scenario: Concurrent subagent streams on 2-account `gemini-4-argon` pool proceed without lease saturation 503
- **WHEN** `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` is `"false"` and concurrent streaming requests target `gemini-4-argon*` across the three entitled `Ultra` `agy` accounts
- **THEN** OmniRoute SHALL allow concurrent streams on the three entitled `Ultra` `agy` accounts without returning `503 All eligible Antigravity accounts are currently handling a request for this model`

#### Scenario: Permanently banned OAuth subscription account automatically quarantined
- **WHEN** an OAuth/subscription connection (`agy`, `github`, `muse-code`) receives a permanent ban classification (`permanent: true`) while `auto-disable-accounts` is enabled with `scope: "subscription"`
- **THEN** OmniRoute SHALL set `isActive: false` and stamp `banDisabledAt` on that connection while leaving `apikey`-authenticated connections unaffected

### Requirement: Gemini 4 Trailing Model Turn Stripping, Exact-Model Lockout Scoping on agy, Slow SQLite Telemetry, and Unified Database Semantic Cache Config

The OmniRoute gateway SHALL strip trailing `role: "model"` turns on `gemini-4-*` requests, SHALL exclude `"model turn"` HTTP 400 responses from model-access-denied lockout classifiers, SHALL scope `agy` per-model lockouts to the exact model, and SHALL configure `OMNIROUTE_SQLITE_SLOW_MS=200` with unified `database_settings.cache` limits.

#### Scenario: Trailing model turn stripped on gemini-4-argon requests
- **WHEN** a coding client or advisor submits a request targeting `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low` whose translated Gemini `contents` array ends with one or more `role: "model"` entries (and `contents.length > 1`)
- **THEN** OmniRoute SHALL strip the trailing `role: "model"` entries before sending the payload to Cloud Code so upstream does not reject the turn with HTTP 400

#### Scenario: Request-shape model-turn 400 does not trigger 1-hour model_capacity lockout
- **WHEN** an upstream target returns HTTP 400 with `"Requests ending with a model turn are not supported"`
- **THEN** both `isModelScoped400` and `isProviderModelUnsupported400` SHALL return `false` and OmniRoute SHALL NOT lock the model or `family:gemini` for 1 hour (`model_capacity`)

#### Scenario: Per-model lockouts on agy connections scope to the exact model
- **WHEN** `lockModelIfPerModelQuota` records a per-model lockout for provider `"agy"`
- **THEN** OmniRoute SHALL invoke `lockExactModel` for the specific model ID rather than locking the entire `family:gemini` quota family across the connection

#### Scenario: Synchronous SQLite stall telemetry and unified database semantic cache settings
- **WHEN** `OMNIROUTE_SQLITE_SLOW_MS=200` is configured and `/api/settings/database` is queried
- **THEN** OmniRoute SHALL emit a diagnostic `[SQLITE-SLOW]` warning (without query parameters or prompt content) whenever a synchronous SQLite operation exceeds 200 milliseconds, and `GET /api/settings/database` SHALL report `cache.semanticCacheMaxSize: 1000` and `cache.semanticCacheTTL: 18000000` matching `GET /api/settings`

### Requirement: Internal Qdrant Sidecar Deployment and Scalar int8 Vector Quantization

OmniRoute SHALL run an internal `omniroute-qdrant` (`qdrant/qdrant:v1.12.4`) sidecar bound exclusively to `127.0.0.1:6333` and `127.0.0.1:6334` with persistent named volume `omniroute-qdrant-data`, configure `/api/settings/qdrant` (`enabled: true`, `host: "qdrant"`, `port: 6333`, `collection: "omniroute_memory"`, `embeddingModel: "voyage-ai/voyage-code-3"`, `quantization: "int8"`), and set `QDRANT_VECTOR_SIZE=1024` and `QDRANT_HNSW_EF_CONSTRUCT=128`.

#### Scenario: Qdrant health and collection configuration on local and internal networks
- **WHEN** `GET /api/settings/qdrant` and `GET /api/memory/engine-status` are queried while `omniroute-qdrant` is running
- **THEN** `GET /api/settings/qdrant` SHALL report `enabled: true`, `host: "qdrant"`, `port: 6333`, `collection: "omniroute_memory"`, `embeddingModel: "voyage-ai/voyage-code-3"`, and `quantization: "int8"`, and `GET /api/memory/engine-status` SHALL report `qdrant.enabled: true` and `qdrant.healthy: true` without exposing port `6333` or `6334` on Tailscale Serve or non-loopback host interfaces

#### Scenario: Dual-tier int8 quantization across Qdrant and sqlite-vec fallback
- **WHEN** a memory entry is created or updated via `POST /api/memory` or post-response extraction with `MEMORY_VEC_QUANTIZATION=int8` and `QDRANT_VECTOR_SIZE=1024` enabled
- **THEN** OmniRoute SHALL upsert the `1024`-dimensional `voyage-ai/voyage-code-3` vector into Qdrant with scalar `int8` quantization (`always_ram: true`, `rescore: true`) and into local SQLite `vec_memories` (`int8[1024]`) as the automatic Tier-1 fallback

### Requirement: Always-On Hybrid Memory with Qdrant Cosine, FTS5 BM25 RRF Fusion, and Cross-Encoder Reranking

OmniRoute SHALL configure `/api/settings/memory` with `enabled: true`, `maxTokens: 2000`, `retentionDays: 60`, `strategy: "hybrid"`, `skillsEnabled: false`, `embeddingSource: "remote"`, `embeddingProviderModel: "voyage-ai/voyage-code-3"`, `rerankEnabled: true`, `rerankProviderModel: "voyage-ai/rerank-2.5"`, and `vectorStore: "qdrant"`, and SHALL fuse Qdrant Cosine hits with SQLite `memory_fts` BM25 hits via Reciprocal Rank Fusion (`k = 60`) before reranking.

#### Scenario: Hybrid retrieval fuses Qdrant vector ranks and SQLite FTS5 BM25 ranks with reranking
- **WHEN** `POST /api/memory/retrieve-preview` or chat memory injection runs under `strategy: "hybrid"` and `vectorStore: "qdrant"`
- **THEN** OmniRoute SHALL execute both Qdrant Cosine search (`omniroute_memory`) and SQLite `memory_fts` BM25 search (including when Qdrant returns 0 vector hits while `memory_fts` matches), combine their candidate rankings using Reciprocal Rank Fusion (`rrf_score = 1/(60 + r_qdrant) + 1/(60 + r_fts)`), and rerank the fused candidates via loopback `POST /v1/rerank` using `voyage-ai/rerank-2.5` while leaving `strategy: "semantic"` as pure vector search

#### Scenario: Graceful fallback to sqlite-vec and FTS5 hybrid RRF when Qdrant is unreachable
- **WHEN** `omniroute-qdrant` is unreachable or returns an error during `strategy: "hybrid"` retrieval
- **THEN** OmniRoute SHALL fail open to Tier-1 `sqlite-vec` (`vec_memories`) + `memory_fts` BM25 RRF fusion without failing the inference request

#### Scenario: Always-on memory owner resolution across keyless and API-key local and remote requests
- **WHEN** a local loopback client (`127.0.0.1:20128`/`20129`) or remote Tailnet client (`https://iosteam-mac-mini.tailc6b508.ts.net`) submits a chat or Responses API request without `x-omniroute-no-memory: true`
- **THEN** OmniRoute SHALL resolve `memoryOwnerId` and semantic cache `apiKeyId` to `apiKeyInfo.id` when an API key is present or `OMNIROUTE_DEFAULT_OWNER_ID` (`"6a72d8ab-88db-4d49-973b-864c6cbdace5"`) when keyless, performing both pre-request hybrid memory retrieval and post-response fact extraction without mutating `body.tools` unless `x-omniroute-no-memory: true` is supplied

### Requirement: All-Request Layer-2 Redis Semantic Cache with Host Ollama Embeddings and Output-Contract Partitioning

OmniRoute SHALL configure `/api/settings/cache-config` with `semanticCacheEnabled: true`, `semanticCacheVectorEnabled: true`, `semanticCacheBackend: "redis"`, `semanticCacheRedisUrl: "redis://redis:6379"`, `semanticCacheThreshold: 0.90`, `semanticCacheEmbeddingProvider: "ollama-local"`, `semanticCacheEmbeddingModel: "nomic-embed-text"`, `semanticCacheEmbeddingDimension: 768`, and `semanticCacheEmbeddingBaseUrl: "http://host.docker.internal:11434/v1/embeddings"`.

#### Scenario: Semantic cache hits across requests carrying tools, reasoning_effort, or max_tokens with identical output contracts
- **WHEN** two `temperature: 0` requests with semantically equivalent prompts (`cosine similarity >= 0.90`, up to 10 turns) and identical `outputContractOf(body)` (`tools`, `tool_choice`, `max_tokens`, `reasoning_effort`, `response_format`, `text.format`) are submitted
- **THEN** OmniRoute SHALL partition the Redis vector lookup and store by the SHA-256 digest of `outputContractOf(body)` rather than bypassing Layer-2, returning a semantic cache `HIT` (`X-OmniRoute-Cache: HIT`, `X-OmniRoute-Cache-Similarity`) on the second request

#### Scenario: Requests with different tool schemas or output formats never collide in Layer-2 semantic cache
- **WHEN** a request with `tools` or `response_format` schema `A` follows a semantically similar prompt that was cached under schema `B` (`A != B`)
- **THEN** OmniRoute SHALL isolate their Redis vector partitions by contract digest and SHALL NOT serve schema `B`'s cached response to schema `A`'s request

#### Scenario: Registry baseUrl fallback for cloud embedding providers in semantic cache probe
- **WHEN** `POST /api/settings/cache-config/test-embedding` or `SemanticCacheDbBridge` resolves an embedding provider whose SQLite `provider_connections` row has no custom `provider_specific_data.baseUrl` (such as `voyage-ai`, `jina-ai`, or `openrouter`)
- **THEN** OmniRoute SHALL fall back to the provider's canonical `EMBEDDING_PROVIDERS[provider].baseUrl` while preserving its stored API key

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

### Requirement: Three-Ultra-Account Gemini-4-Argon Combo Routing

OmniRoute SHALL configure `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` combos with explicit connection-scoped model steps (`kind: "model"`, `providerId: "agy"`, `weight: 0`, and non-empty account email `label`) for all 3 active Google AI Ultra Antigravity accounts (`62af823b-f3d7-4e6b-87a9-98069167d4f6` / `vicgnome19094@gmail.com`, `0532bad4-2486-4286-8f06-510e9c678620` / `vinhvumobile@gmail.com`, `338764b8-1cd7-4946-b789-ee5dad4c5073` / `vinhghtk1908@gmail.com`), preserving `strategy: "auto"`, `context_cache_protection: false`, and `config.targetTimeoutMs: 180000`.

#### Scenario: All three Ultra accounts present in every gemini-4-argon* combo
- **WHEN** `GET /api/combos/{id}` is queried for `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low`
- **THEN** `models` SHALL contain 3 steps mapped to `connectionId` values `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`label: "vicgnome19094@gmail.com"`), `0532bad4-2486-4286-8f06-510e9c678620` (`label: "vinhvumobile@gmail.com"`), and `338764b8-1cd7-4946-b789-ee5dad4c5073` (`label: "vinhghtk1908@gmail.com"`)
- **AND** `strategy` SHALL be `"auto"`, `context_cache_protection` SHALL be `false`, and `config.targetTimeoutMs` SHALL be `25000`

#### Scenario: Live gemini-4-argon inference succeeds with 3 Ultra accounts
- **WHEN** a completion request is sent to `gemini-4-argon` or `gemini-4-argon-high` (or when one Ultra account returns `HTTP 429`)
- **THEN** OmniRoute SHALL route across the 3 Ultra accounts with `HTTP 200` and bound any single stalled upstream target attempt to `180,000 ms`

### Requirement: Multi-Agent Heavyweight Chat Admission Concurrency and Composite-Combo Prune Protection

OmniRoute SHALL configure `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16` and `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=15000` in `/Users/androidteam/Omniroute/.env` and SHALL persist `COMBO_AUTO_PRUNE_STALE_STEPS` as `"false"` in SQLite `feature_flags` so concurrent tool-bearing subagent streams do not shed with `HTTP 503 chat_admission_busy` and composite combos containing a `combo-ref` fallback retain their explicit model steps across catalog syncs.

#### Scenario: Concurrent tool-bearing subagent turns admit without 503 chat_admission_busy
- **WHEN** up to 16 concurrent tool-bearing coding-agent requests (`tools.length >= 64` or `content-length >= 256 KB`) arrive at `/v1/chat/completions` or `/v1/responses` while total `inflightBytes` is below `137,363,456` bytes
- **THEN** `ChatAdmissionController` SHALL admit the requests to the combo router without returning `HTTP 503 chat_admission_busy`

#### Scenario: Composite combo with trailing `combo-ref` retains explicit model steps across catalog syncs
- **WHEN** `COMBO_AUTO_PRUNE_STALE_STEPS` is `"false"` in `GET /api/settings/feature-flags` and scheduled provider model sync runs
- **THEN** OmniRoute SHALL preserve all explicit `kind: "model"` steps in `claude-opus-5.5` ahead of its `combo-ref: gemini-3.8-flash-high` fallback
