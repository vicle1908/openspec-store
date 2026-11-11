# omniroute-compression-and-routing Specification

## Purpose

Defines the operational behavior, token compression rules, combo routing resilience invariants, thinking-budget passthrough policy, and feature-flag baseline for the OmniRoute AI gateway (`v3.8.52`) when serving multi-turn coding agents over loopback interfaces.

## Requirements

### Requirement: RTK Tool Result Compression, Adaptive Context Budget, and Delegated Context Editing

The OmniRoute gateway SHALL configure RTK compression at `minimal` intensity for tool result payloads while preserving system prompts and code blocks, SHALL preserve OpenAI Responses `function_call` tool metadata and set `_rtkSkip = true` for all non-shell tools so only shell execution tools run RTK log filters, SHALL configure `contextBudget.mode` as `"replace-autotrigger"` (`pct: 0.85`), and SHALL enable delegated `contextEditing` for supported Claude relays.

#### Scenario: Verbose tool output compressed before upstream dispatch
- **WHEN** a coding client submits a request carrying `x-omniroute-compression: allow-lossy` or `engine:rtk` (or tests via `POST /api/context/rtk/test` with an explicit `command`) containing a tool result matching one of the 55 built-in RTK filters
- **THEN** OmniRoute SHALL compress the tool result payload within `maxLinesPerResult` (120) and `maxCharsPerResult` (12000) bounds while preserving system prompts (`preserveSystemPrompt: true`) and code blocks (`applyToCodeBlocks: false`) verbatim

#### Scenario: Headerless requests honor safe default pipeline and adaptive context budget escalation
- **WHEN** a client submits a request without an `x-omniroute-compression` header
- **THEN** OmniRoute SHALL run its server-side tool-safe `[session-dedup, lite, rtk, codex-responses, headroom]` stack (`compressionComboId: "default-caveman"`, `caveman: false`, `lite.compressToolResults: false`) when below the 85% `contextBudget` threshold, and `resolveAdaptivePlan` SHALL escalate along the compression ladder when estimated input tokens exceed the `contextBudget` target

#### Scenario: OpenAI Responses non-shell tool outputs bypass RTK content filters
- **WHEN** an OpenAI Responses client (`api: "openai-responses"`) submits `body.input` containing a `type: "function_call"` item (`name: "read"`, `"glob"`, `"grep"`, `"write"`, `"edit"`, `"eval"`, `"task"`, `"todo"`, `"find"`, `"ask"`, `"lsp"`, `"ast_grep"`, `"ast_edit"`, or any non-shell tool) paired by `call_id` with a `type: "function_call_output"` item
- **THEN** `adaptBodyForCompression()` SHALL attach `tool_call_id`, skip the `b.find(...)` and `JSON.parse(...)` command extraction when `_sh` is `false` (`_fc=_sh&&k?b.find(...):null`), and set `_rtkSkip: true` whenever the paired `function_call` `name` does not match `/\b(bash|shell|terminal|run_command|execute_command|exec|command)\b/i` (or is listed in `codexResponsesConfig.preserveToolNames`)
- **AND** `rtk` SHALL honor `_rtkSkip === true` (`skipFilters: true`) even after `adaptBodyForCompression()` deletes `body.input`, preserving structured and file-read outputs verbatim without line stripping

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
- **THEN** OmniRoute SHALL execute `gemini-3.8-flash-high` as an encapsulated runtime unit (`nestedComboMode: "execute"`) using its `auto` strategy before falling back to `agy/gemini-3.8-flash-medium`, while `claude-opus-5.5` (`strategy: "auto"`, `nestedComboMode: "flatten"`) SHALL score all 15 Antigravity accounts via 16-factor `auto` routing and `applySessionStickiness`

### Requirement: Thinking Budget Passthrough and Resilience Feature Flags

OmniRoute SHALL configure `thinkingBudget.mode` as `"passthrough"` and SHALL enable the v3.8.52 resilience feature flags `CREDENTIAL_GATE_AUTH_DIAGNOSES_ONLY`, `COMBO_EMPTY_POOL_NO_ELIGIBLE_TARGETS_ENABLED`, `STREAM_LATE_OUTPUT_PROBE_ENABLED`, and `RETRY_AFTER_PROVENANCE_ENABLED` via individual string-valued (`"true"`) flag overrides while keeping `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` as `"false"`.

#### Scenario: Client reasoning parameters preserved under passthrough mode
- **WHEN** Codex CLI, Claude Code, or OMP sends a request containing `reasoning`, `reasoning_effort`, `thinking`, or `thinking_config`
- **THEN** OmniRoute SHALL preserve those fields verbatim without stripping or overwriting them

#### Scenario: Antigravity concurrent account lease disabled on small pools
- **WHEN** `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` is `"false"` in SQLite `key_value` (`namespace = 'feature_flags'`)
- **THEN** concurrent streaming requests across small account pools (`gemini-4-argon*`) SHALL route without shedding with HTTP 503 `POOL_BUSY`

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

#### Scenario: Headerless multi-turn requests preserve prior-turn `Read` and `Grep` tool results under server-side tool-safe pipeline
- **WHEN** a coding client submits a multi-turn request without an `x-omniroute-compression` header and with prior-turn tool results exceeding 2,000 characters
- **THEN** OmniRoute SHALL run its tool-safe `[session-dedup, lite, rtk, codex-responses, headroom]` pipeline and `lite` SHALL NOT truncate prior-turn tool results to 2,000 characters (`compressToolResults: false`)
#### Scenario: Lossy-opt-in and `codex-responses` requests compress `/v1/responses` and `/v1/chat/completions` tool outputs while protecting file reads
- **WHEN** a request opts into lossy compression (`x-omniroute-compression: allow-lossy`, `engine:codex-responses`, or `engine:rtk`) or invokes `ladderOverride` (`basePlan.mode === "off"` at >85% `percentage` context budget)
- **THEN** OmniRoute SHALL execute `codex-responses` (on `/v1/responses` `function_call_output` items, protecting `Read`, `Glob`, `Grep`, `Write`, `Edit`, `WebSearch`, `WebFetch`, `find`) and `rtk` (`minimal` intensity on tool results)

### Requirement: Bounded Quota Park, Early-EOF Sibling Failover, Refusal Cooldown Skip, and Terminal Safety Stops
OmniRoute SHALL persist 24 enabled v3.8.52 resilience, routing, catalog, and compaction feature flags as "true" and ANTIGRAVITY_ACCOUNT_LEASE_ENABLED and COMBO_AUTO_PRUNE_STALE_STEPS as "false" in SQLite key_value (namespace='feature_flags'), set mcpDescriptionCompressionEnabled to true, set sessionAffinityTtlMs to 300000, and keep FLUSH_EMPTY_RETRY_ENABLED and OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS disabled ("false") while OMNIROUTE_ALLOW_LOCAL_PROVIDER_URLS remains "true".

#### Scenario: Pre-first-frame SSE early EOF fails over once to a sibling connection
- **WHEN** `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED` is `true` and an upstream SSE stream closes with `STREAM_EARLY_EOF` before emitting any useful frame
- **THEN** OmniRoute SHALL exclude the failed connection and retry once on an eligible sibling connection

#### Scenario: Content-policy safety refusal stops combo retry loop
- **WHEN** `PROVIDER_SAFETY_STOPS_TERMINAL` and `CONTENT_POLICY_REFUSAL_COMBO_STOP_ENABLED` are `true` and an upstream target returns HTTP 400 or 403 with `content_policy_violation`, `cyber_policy`, or `misalignment_policy_violation`
- **THEN** OmniRoute SHALL treat the refusal as terminal for the request and SHALL NOT retry the refused prompt across remaining combo targets

#### Scenario: Expanded v3.8.52 coding-agent feature flags and MCP description compression resolve from authoritative SQLite tables
- **WHEN** `GET /api/settings/feature-flags` and `GET /api/settings/compression` are queried with management authentication
- **THEN** all 24 enabled flags (`QUOTA_WINDOW_BOUNDED_PARK`, `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED`, `COOLDOWN_RETRY_SKIP_REFUSALS_ENABLED`, `PROVIDER_SAFETY_STOPS_TERMINAL`, `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED`, `STREAM_READINESS_STALL_RETRY`, `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED`, `STREAM_LATE_OUTPUT_PROBE_ENABLED`, `RETRY_AFTER_PROVENANCE_ENABLED`, `COMBO_EMPTY_POOL_NO_ELIGIBLE_TARGETS_ENABLED`, `CREDENTIAL_GATE_AUTH_DIAGNOSES_ONLY`, `AUTO_REQUEST_RESOLVED_CAPABILITIES`, `AUTO_COMBO_KEYLESS_TRANSPORT_GATE`, `MODELS_DEV_EFFORT_TIERS_ENABLED`, `CATALOG_MIRROR_REFINEMENTS_ENABLED`, `ANTHROPIC_COMPATIBLE_MID_CONVERSATION_SYSTEM`, `CONTENT_POLICY_REFUSAL_COMBO_STOP_ENABLED`, `CREDENTIAL_HEALTH_RETEST_AUTO_DISABLED`, `MODEL_ENDPOINT_CAPABILITY_GATE_ENABLED`, `OPENCODE_FULL_TEXT_ERROR_RULES_ENABLED`, `CLOUDFLARE_AI_FULL_TEXT_ERROR_RULES_ENABLED`, `PROTECTED_PRIORITY_INFRA_502_ENABLED`, `NATIVE_CODEX_REACTIVE_COMPACTION_ENABLED`, `CLAUDE_OAUTH_SUMMARIZED_THINKING_UNREDACTED`) SHALL report `effectiveValue: "true"` and `source: "db"`, `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` and `COMBO_AUTO_PRUNE_STALE_STEPS` SHALL report `effectiveValue: "false"` and `source: "db"`, and `GET /api/settings/compression` SHALL report `mcpDescriptionCompressionEnabled: true`

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

### Requirement: Predictive TTFT Circuit Breaker, Unleased 3-Ultra-Account Pool Concurrency, and Subscription-Scoped Ban Auto-Disable
OmniRoute SHALL enable `zeroLatencyOptimizationsEnabled: true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) in `/api/settings/combo-defaults` and as the default baseline for `agy` combos while preserving explicit higher-latency tier overrides, SHALL isolate per-attempt target latency across direct metrics and retry helpers, and SHALL scope predictive TTFT to individual targets with bounded recovery and starvation guards.

#### Scenario: Stalled target exceeding 25-second average latency skipped on attempt 0 without fallback re-truncation
- **GIVEN** `zeroLatencyOptimizationsEnabled` is `true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`, or the combo's tier-matched `predictiveTtftMs` and `targetTimeoutMs` override) and a connection target's `avgLatencyMs` in `getComboMetrics` (`byTarget[executionKey]`) exceeds the combo's configured `predictiveTtftMs` threshold over at least 5 requests within an active 120,000-millisecond predictive cooldown window
- **WHEN** a new combo request evaluates that target while at least one other eligible unreserved candidate remains in the combo
- **THEN** OmniRoute SHALL skip that target on primary attempt `0` (`predictive_ttft`) and dispatch to the next eligible candidate without issuing duplicate speculative hedged requests or running unconfigured fallback `lite` truncation

#### Scenario: Failover target latency isolated from prior target timeouts and empty-content helper retries
- **GIVEN** target `0` in a combo fails or times out (for example after 25,000 milliseconds) and the combo fails over to target `1`
- **WHEN** target `1` completes in `L` milliseconds, either directly or through helper retry paths including `handleEmptyContentRetry`
- **THEN** OmniRoute SHALL record target `1`'s latency in `byTarget` and `byModel` (and evaluate any helper retry elapsed time for target `1`) from target `1`'s own attempt start timestamp (`L` milliseconds) rather than cumulative combo elapsed time since target `0` started, while preserving whole-request elapsed timing at the outer combo loop

#### Scenario: Connection-scoped predictive evaluation isolates untried sibling accounts from shared model averages
- **GIVEN** a multi-account combo where connection-scoped targets (`executionKey !== modelStr`) share a common `modelStr` and shared `byModel[modelStr].avgLatencyMs` exceeds the combo's `predictiveTtftMs` threshold
- **WHEN** OmniRoute evaluates `predictiveTtftMs` for a sibling connection whose `byTarget[executionKey]` is absent or has fewer than 5 recorded requests
- **THEN** OmniRoute SHALL evaluate `predictiveTtftMs` strictly against `byTarget[executionKey]` without falling back to `byModel[modelStr]` and SHALL NOT skip the untried or under-sampled sibling connection on account of another connection's latency

#### Scenario: Post-cooldown single-probe reservation, latency window re-seed, and terminal release
- **GIVEN** a connection target whose `byTarget[executionKey]` has at least 5 requests with `avgLatencyMs` exceeding `predictiveTtftMs` and whose 120,000-millisecond predictive cooldown window has elapsed
- **WHEN** concurrent requests arrive for that combo
- **THEN** OmniRoute SHALL atomically reserve at most one in-flight recovery probe for that `(comboName, executionKey)` in authoritative metrics state before upstream dispatch while concurrent requests skip that target until the reservation settles
- **AND** if the recovery probe fails, aborts, times out, or succeeds above the predictive threshold, OmniRoute SHALL retain the 90,000-millisecond single-flight reservation lock in `__omniProbeAt` to prevent concurrent probe stampedes and maintain predictive cooldown protection
- **AND** if the recovery probe succeeds with latency at or below `predictiveTtftMs`, OmniRoute SHALL release the reservation and re-seed that target's predictive latency window from the probe duration so cumulative pre-cooldown timeouts do not immediately re-trip `predictive_ttft`, while preserving lifetime request and failure counters

#### Scenario: Eligible-candidate starvation guard respects independent eligibility gates
- **GIVEN** a combo request where all candidates except one otherwise-eligible unreserved candidate have been skipped by `predictive_ttft`, including when the final raw index in `orderedTargets` is independently blocked by auth, quota, model lockout, provider cooldown, or concurrency gates
- **WHEN** OmniRoute evaluates predictive latency for the last remaining candidate that passed all independent eligibility gates (`recordedAttempts === 0`)
- **THEN** OmniRoute SHALL dispatch to that last eligible unreserved candidate rather than returning a zero-attempt `503` from predictive filtering alone, and SHALL NEVER bypass auth, quota, model lockout, cooldown, or concurrency gates on an ineligible target

#### Scenario: Per-target auto candidate scoring and coherent scoped combo metrics state
- **GIVEN** a multi-account `auto` combo with per-target runtime history in `byTarget[executionKey]`
- **WHEN** `buildAutoCandidates` scores candidate targets or an operator queries or resets metrics for an affected combo (`GET /api/combos/metrics` or `DELETE /api/combos/metrics?combo=<name>`)
- **THEN** `buildAutoCandidates` SHALL prefer `byTarget[executionKey]` latency and success rate whenever `byTarget[executionKey].requests > 0` (using `byModel[modelStr]` or 24-hour model aggregates only as fallback when target history is absent)
- **AND** routing, metrics inspection, and scoped combo resets (`DELETE /api/combos/metrics?combo=<name>`) SHALL operate on the same active in-memory metrics state without clearing unrelated combo metrics or stopping the periodic metrics cleanup timer

#### Scenario: Concurrent subagent streams on 3-Ultra-account `gemini-4-argon` pool proceed without lease saturation 503
- **WHEN** `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` is `"false"` and concurrent streaming requests target `gemini-4-argon*` across the three entitled `Ultra` `agy` accounts
- **THEN** OmniRoute SHALL allow concurrent streams on the three entitled `Ultra` `agy` accounts without returning `503 All eligible Antigravity accounts are currently handling a request for this model`

#### Scenario: Permanently banned OAuth subscription account automatically quarantined
- **WHEN** an OAuth/subscription connection (`agy`, `github`, `muse-code`) receives a permanent ban classification (`permanent: true`) while `auto-disable-accounts` is enabled with `scope: "subscription"`
- **THEN** OmniRoute SHALL set `isActive: false` and stamp `banDisabledAt` on that connection while leaving `apikey`-authenticated connections unaffected

### Requirement: Gemini 4 Trailing Model Turn Stripping, Exact-Model Lockout Scoping on agy, Slow SQLite Telemetry, and Unified Database Semantic Cache Config
The OmniRoute gateway SHALL strip trailing `role: "model"` turns on `gemini-4-*` requests, SHALL exclude `"model turn"` HTTP 400 responses from lockout classifiers, SHALL enable `settings.modelLockout` scoping `agy` lockouts to the exact model, SHALL enforce file-scoped startup patch replacements and per-file markers in `/app/container-entrypoint-compat.sh`, and SHALL configure `OMNIROUTE_SQLITE_SLOW_MS=200`.

#### Scenario: Trailing model turn stripped on gemini-4-argon requests
- **WHEN** a coding client or advisor submits a request targeting `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low` whose translated Gemini `contents` array ends with one or more `role: "model"` entries (and `contents.length > 1`)
- **THEN** OmniRoute SHALL strip the trailing `role: "model"` entries before sending the payload to Cloud Code so upstream does not reject the turn with HTTP 400

#### Scenario: Request-shape model-turn 400 does not trigger 1-hour model_capacity lockout
- **WHEN** an upstream target returns HTTP 400 with `"Requests ending with a model turn are not supported"`
- **THEN** both `isModelScoped400` and `isProviderModelUnsupported400` SHALL return `false` and OmniRoute SHALL NOT lock the model or `family:gemini` for 1 hour (`model_capacity`)

#### Scenario: Per-model lockouts on agy connections scope to the exact model
- **GIVEN** `settings.modelLockout.enabled` is `true` (`errorCodes: [403, 404, 429, 502, 503, 504]`, `baseCooldownMs: 120000`, `maxCooldownMs: 1800000`, `maxBackoffSteps: 10`, `useExponentialBackoff: true`)
- **WHEN** `lockModelIfPerModelQuota` or `recordModelLockoutFailure` records a per-model lockout (such as HTTP 429 or synthetic HTTP 504 `combo_target_timeout`) for provider `"agy"` or `"antigravity"`, including when invoked from combo failure handling without an explicit `options.scope` override
- **THEN** OmniRoute SHALL resolve the lockout scope to `"exact"` and invoke `lockExactModel` for the specific `<provider>:<connectionId>:exact:<model>` tuple so subsequent requests skip that timed-out or rate-limited connection for that exact model during its cooldown window rather than locking the entire `family:gemini` or `family:claude` quota family across the connection

#### Scenario: File-scoped startup patch execution and per-file marker verification fail closed
- **GIVEN** `/app/container-entrypoint-compat.sh` applies runtime compatibility replacements and validates `requiredMarkers` on container startup
- **WHEN** any replacement rule is executed or `requiredMarkers` are checked across target server bundles
- **THEN** each replacement rule SHALL execute only against its explicitly scoped target file or unique surrounding context (preventing cross-chunk helper identifier collisions), repeated runs SHALL be idempotent, and startup verification SHALL enforce `fileMatch` suffix matching for every required marker and exit non-zero (`1`) if any target file is missing its expected patched state

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

OmniRoute SHALL separate configuration across SQLite runtime tables, ~/Omniroute/.env, and a structural ~/Omniroute/docker-compose.override.yml with zero environment overrides, aligning overlapping semantic-cache keys across .env and SQLite and sizing omniroute-base with OMNIROUTE_MEMORY_MB=4096, container mem_limit: 5g, and multi-agent heavyweight admission (OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16) within the 6 GiB Docker Desktop VM.

#### Scenario: Bounded V8 heap, 5 GiB container cgroup limit, and heavyweight admission within the 6 GiB Docker VM
- **WHEN** `omniroute-base` starts with `OMNIROUTE_MEMORY_MB=4096` and `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16` in `.env` and `mem_limit: 5g` in `docker-compose.override.yml` on the `6144` MiB (`MemTotal = 6,210,043,904` bytes) Docker Desktop VM
- **THEN** `/app/check-permissions.sh` SHALL configure `v8.getHeapStatistics().heap_size_limit` (`4,395,630,592` bytes) strictly below `process.constrainedMemory()` (`5,368,709,120` bytes / `5g`), which in turn SHALL remain below Docker VM `MemTotal` (`6,210,043,904` bytes), and `GET /api/monitoring/health` SHALL report `chatAdmission.countCapEnabled: true`, `chatAdmission.budgetSource: "v8_heap"`, and `chatAdmission.maxInflightBytes: 137363456`

#### Scenario: Structural docker-compose.override.yml preserves service identities, healthcheck timing, and zero environment overrides
- **WHEN** `/Users/androidteam/Omniroute/docker-compose.override.yml` and `docker compose --profile base config` are inspected
- **THEN** `docker-compose.override.yml` SHALL contain zero `environment:` entries and only structural service overrides (Hub image `diegosouzapw/omniroute:latest`, explicit `mem_limit`, `extra_hosts` for `host.docker.internal`, named volume `omniroute-data:/app/data` and `container-entrypoint-compat.sh` mount, healthcheck `timeout: 15s` and `start_period: 120s`, `redis` `ports: !reset []`, and `qdrant` `profiles: !override [base, memory]` + `/dev/tcp` healthcheck) while preserving container identities `omniroute`, `omniroute-redis`, and `omniroute-qdrant`

#### Scenario: Cold-start Responses and Messages requests initialize semantic cache without management warmup and isolate tool contracts
- **WHEN** `omniroute` starts fresh and serves cold-start `POST /v1/responses` or `POST /v1/messages` requests before `/api/settings/cache-config` or `/v1/chat/completions` has been called
- **THEN** `SemanticCacheManager` SHALL initialize from the synchronized `OMNIROUTE_SEMANTIC_CACHE_*` variables in `.env` (returning `X-OmniRoute-Cache: HIT` on a repeated `temperature: 0` request with identical output and tool contracts) and SHALL return `X-OmniRoute-Cache: MISS` when `tools`, `tool_choice`, `response_format`, or tool-history digests differ

### Requirement: Three-Ultra-Account Gemini-4-Argon Combo Routing
OmniRoute SHALL configure `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` combos with explicit connection-scoped model steps for all 3 active Google AI Ultra Antigravity accounts (`62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, `338764b8-1cd7-4946-b789-ee5dad4c5073`), preserving `strategy: "auto"` and setting `context_cache_protection: false`.

#### Scenario: All three Ultra accounts present in every gemini-4-argon* combo
- **WHEN** `GET /api/combos/{id}` is queried for `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low`
- **THEN** `models` SHALL contain 3 steps mapped to `connectionId` values `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`label: "vicgnome19094@gmail.com"`), `0532bad4-2486-4286-8f06-510e9c678620` (`label: "vinhvumobile@gmail.com"`), and `338764b8-1cd7-4946-b789-ee5dad4c5073` (`label: "vinhghtk1908@gmail.com"`)
- **AND** `strategy` SHALL be `"auto"`, `context_cache_protection` SHALL be `false`, `config.targetTimeoutMs` SHALL be `180000`, and `config.predictiveTtftMs` SHALL be `60000`

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
- **THEN** OmniRoute SHALL preserve all explicit `kind: "model"` steps in composite combos containing a `combo-ref` step (such as `muse-spark-1.3`) alongside all 15 explicit `kind: "model"` steps in `claude-opus-5.5`

### Requirement: Multi-Account Claude Opus and Sonnet Combo Pooling across Antigravity Accounts
OmniRoute SHALL configure `claude-opus-5.5` and `claude-sonnet-5.5` combos to pool all 13 active Antigravity connections (`10` Pro and `3` Ultra, excluding banned `47f334b1`, `d5c3465f`, and `20369f65`) across 13 `kind: "model"` steps matching each account's `syncedAvailableModels` catalog with `0` `combo-ref` steps, `context_length: 1000000`, `strategy: "auto"`, and `context_cache_protection: false`.

#### Scenario: Claude Opus 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`)
- **THEN** OmniRoute SHALL return a combo with 13 explicit `kind: "model"` steps matching each active connection's `syncedAvailableModels` entry (`agy/claude-opus-5-5-high` on migrated connection `38782750-7a60-46d4-ae3f-e8c13cda296b` and `agy/claude-opus-4-6-thinking` on the remaining 12 active `agy` connections, excluding banned `47f334b1`, `d5c3465f`, and `20369f65`, with `0` `combo-ref` steps), `context_length: 1000000`, `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`

#### Scenario: Claude Sonnet 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** OmniRoute SHALL return a combo with 13 explicit `kind: "model"` steps matching each active connection's `syncedAvailableModels` entry (`agy/claude-sonnet-5-5-high` on migrated connection `38782750-7a60-46d4-ae3f-e8c13cda296b` and `agy/claude-sonnet-4-6` on the remaining 12 active `agy` connections, excluding banned `47f334b1`, `d5c3465f`, and `20369f65`), `context_length: 1000000`, `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Live chat completions route through multi-account Claude combos to authentic Claude models
- **WHEN** `POST /v1/chat/completions` is called with `model: "claude-opus-5.5"` or `model: "claude-sonnet-5.5"`
- **THEN** OmniRoute SHALL return HTTP 200 with a completion served by `claude-opus-5-5-high`/`claude-opus-4-6-thinking` or `claude-sonnet-5-5-high`/`claude-sonnet-4-6` on one of the 13 active Antigravity accounts with zero synthetic deprecation responses or banned-account 403 dispatches

#### Scenario: Upstream Claude 5.5 model cutover contract
- **WHEN** upstream Google Antigravity provisions and advertises `claude-opus-5-5-*` or `claude-sonnet-5-5-*` in its live discovery catalog
- **THEN** OmniRoute SHALL update the explicit model steps in `claude-opus-5.5` and `claude-sonnet-5.5` combos from 4.6 to the corresponding 5.5 identifiers while preserving all active connection mappings

### Requirement: Cached Voyage AI Qdrant Embeddings, Health-Check Point Guard, and FTS5 OR Hybrid Retrieval

OmniRoute SHALL keep Hybrid Memory enabled (`enabled: true`, `skillsEnabled: false`, `strategy: "hybrid"`, `vectorStore: "qdrant"`, `voyage-ai/voyage-code-3`, `voyage-ai/rerank-2.5`), SHALL cache 1024d vectors in `globalThis.__omnirouteQdrantEmbedCache` inside `qdrant.ts:embedText()` (`chunks/54843.js`), SHALL skip Qdrant persistence when `apiKeyId === "health-check"`, and SHALL join FTS5 query tokens with `OR` in `sanitizeFts5Query()`.

#### Scenario: Repeated semantic memory queries hit the in-memory LRU embedding cache without duplicate Voyage AI HTTP calls
- **WHEN** `searchSemanticMemory()` executes for a query text whose `("voyage-ai/voyage-code-3", text)` vector is already present in `globalThis.__omnirouteQdrantEmbedCache`
- **THEN** `qdrant.ts:embedText()` SHALL return the cached 1024-dimension vector in `<1 ms` without issuing an outbound `POST /v1/embeddings` request to `voyage-ai`
- **AND** on a cache miss, `qdrant.ts:embedText()` SHALL store the returned vector in `globalThis.__omnirouteQdrantEmbedCache` so any subsequent retrieval step in the same or later turn reuses the cached vector

#### Scenario: Clean memory seeding populates Qdrant points and `/api/memory/health` leaves zero orphaned points
- **WHEN** `POST /api/memory` seeds a workspace memory and `GET /api/memory/health` runs `verifyExtractionPipeline("health-check")`
- **THEN** the workspace memory SHALL be indexed in both `vec_memories` (`needsReindex: 0`) and Qdrant `omniroute_memory`, while `apiKeyId === "health-check"` probes SHALL NOT leave orphaned points in `omniroute_memory`

#### Scenario: Multi-word prompt matches FTS5 keyword memories via boolean `OR`
- **WHEN** `retrieveHybrid` builds FTS5 keyword candidates via `sanitizeFts5Query(query)` (`chunks/54843.js` module `541915`)
- **THEN** `sanitizeFts5Query` SHALL join sanitized tokens (`length > 2`) with `" OR "` rather than implicit `" "` (`AND`) so memories sharing relevant keywords are ranked by BM25 and fused with Qdrant cosine results via RRF (`k=60`)

### Requirement: Dedicated 11-Pro-Account Auto Pool for `gemini-3.8-flash-high` and Ultra Quota Isolation
OmniRoute SHALL configure `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) with `strategy: "auto"`, `context_cache_protection: false`, `targetTimeoutMs: 25000`, and 9 `kind: "model"` steps scoped exclusively to active `g1-pro-tier` `agy` connections with remaining quota (excluding the 3 Ultra accounts, quota-exhausted `ce95e1cb`, and banned `47f334b1`, `d5c3465f`, `20369f65`).

#### Scenario: `gemini-3.8-flash-high` routes across the 11 Pro accounts without consuming Ultra Gemini quota
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is inspected or invoked
- **THEN** `strategy` SHALL be `"auto"`, `context_cache_protection` SHALL be `false`, and `models` SHALL contain 9 `agy/gemini-3.8-flash-high` steps mapped to healthy `g1-pro-tier` connections (excluding exhausted `ce95e1cb` and banned `47f334b1`, `d5c3465f`, `20369f65`) with non-empty email `label`s
- **AND** none of the 3 `g1-ultra-tier` `connectionId`s SHALL appear in `gemini-3.8-flash-high`

#### Scenario: All 3 Ultra accounts and 11 Pro accounts enforce `rateLimitProtection: true`
- **WHEN** `GET /api/rate-limits` is queried
- **THEN** all 3 `g1-ultra-tier` `agy` accounts and active `g1-pro-tier` `agy` accounts SHALL report `rateLimitProtection: true` and `enabled: true`

### Requirement: Tier-Matched Combo Timeouts, Cold-Start Semantic Cache Bridge, and Fail-Closed Entrypoint Guard
OmniRoute SHALL configure tier-matched timeouts (`180000`/`60000` on `gemini-4-argon*` and `claude-opus-5.5`; `120000`/`45000` with `maxRetries: 1` on `claude-sonnet-5.5`, `kimi-k3.1-pro`, and `deepseek-v4.1-flash`), configure priority failover and dual quota-cache keys on `kimi-k3.1-pro` and `deepseek-v4.1-flash`, auto-invoke `ensureSemanticCacheDbBridge()` on cold starts, and assert all runtime patch markers fail-closed.

#### Scenario: Deep-reasoning and high-TTFT combos enforce tier-matched timeouts without premature 25s aborts
- **WHEN** `GET /api/combos` is queried
- **THEN** `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `claude-opus-5.5` SHALL each have `config.targetTimeoutMs === 180000` and `config.predictiveTtftMs === 60000`
- **AND** `claude-sonnet-5.5`, `kimi-k3.1-pro`, and `deepseek-v4.1-flash` SHALL each have `config.targetTimeoutMs === 120000`, `config.predictiveTtftMs === 45000`, and `config.maxRetries === 1`
- **AND** `kimi-k3.1-pro` and `deepseek-v4.1-flash` SHALL configure `strategy: "priority"`, `config.nestedComboMode: "execute"`, `resetAwareQuotaCacheTtlMs: 300000`, `resetWindowQuotaCacheTtlMs: 300000`, and failover steps to `nx/deepseek-v4-pro` and `combo-ref: gemini-3.8-flash-high`, while `/api/model-capability-overrides` SHALL persist `max_output_tokens` overrides (`65536` on `antigravity/gemini-4-argon-{high,medium,low}`, `128000` on `antigravity/claude-*` and `antigravity/gemini-3.8-flash-*`) so `65536`-configured clients never fail with `65535` `capability_mismatch`

#### Scenario: Entrypoint verification fails closed across all runtime markers and semantic cache bridge initializes on cold start
- **WHEN** `container-entrypoint-compat.sh` runs on container startup
- **THEN** it SHALL verify all patch markers across the compiled server chunks without skipping missing chunk filenames (`process.exit(1)` on any missing marker)
- **AND** `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_TIMEOUT_MS=3000` and `OMNIROUTE_SEMANTIC_CACHE_TTL_MS=18000000` SHALL be set in `/Users/androidteam/Omniroute/.env` with `ensureSemanticCacheDbBridge()` auto-invoked on `/v1/responses` and `/v1/messages` cold starts

### Requirement: Compression Accounting Provenance
Compression accounting SHALL distinguish estimated token reduction from measured usage and billed cost, record the measurement interval and applicable pricing assumptions, and avoid lifetime-volume or minimum-reduction floors as correctness criteria.

#### Scenario: Compression does not reduce a short input
- **WHEN** an eligible input is already compact or a compressor returns unchanged content
- **THEN** accounting SHALL report zero reduction without inventing savings or treating the request as a correctness failure.

#### Scenario: Reporting estimated monetary savings
- **WHEN** a report converts token reduction into an estimated monetary amount
- **THEN** it SHALL state the model, price basis, measurement window, and limitations and SHALL NOT present the estimate as verified avoided billing.

### Requirement: Optional Compression Quality Gate
Additional compression engines SHALL remain evaluation candidates until representative coding and instruction-following cases demonstrate preserved protected content and acceptable answer, tool-call, and latency outcomes. Existing prose-preserving defaults SHALL remain unchanged during evaluation.

#### Scenario: Protected content and prompt prefixes
- **WHEN** an optional compressor is evaluated on instructions, file contents, tool arguments, identifiers, or cacheable prompt prefixes
- **THEN** the evaluation SHALL check the applicable preservation contract and downstream task correctness, and SHALL NOT accept token reduction alone as sufficient proof.

#### Scenario: Model load or compressor failure
- **WHEN** a model cannot load, execution times out, or compression expands the request
- **THEN** verification SHALL check that the supported fallback preserves the request and reports the failure or bypass without claiming successful compression.

### Requirement: Embedding Timeout Path Evidence
The semantic-cache embedding evaluation SHALL identify the effective deadline at each layer of the embedding request and SHALL distinguish it from chat-header and stream-idle deadlines. Longer timeouts SHALL require measured justification rather than blanket increases.

#### Scenario: Outer setting exceeds inner fetch deadline
- **WHEN** an outer embedding timeout is longer than a separate inner HTTP deadline
- **THEN** the report SHALL identify the limiting deadline and SHALL NOT claim that changing the outer setting alone permits a longer operation.

#### Scenario: Slow or unavailable local embedding service
- **WHEN** an embedding service is cold, slow, or unavailable during evaluation
- **THEN** evidence SHALL record elapsed time, cache-bypass behavior, request outcome, and any uncancelled work; a five-minute chat timeout SHALL NOT substitute for embedding-path verification.

### Requirement: Cache and Coordination Isolation Evaluation
Before changing cache scope or Redis eviction policy, the evaluation SHALL classify enabled cache and coordination consumers and verify request isolation across owners, system policies (`sp:<sha256_16>` covering `body.system`, `body.instructions`, `body.systemInstruction`, and `messages[]` system/developer turns), tool contracts (`ct:<sha256_16>`), tool history (`tc:<sha256_16>`), and freshness state, as well as the effect of memory pressure on rate limits, quotas, and coordination state.

#### Scenario: Similar prompts with different request context
- **WHEN** similar requests differ in authorized owner, system policy (`body.system`, `body.instructions`, `body.systemInstruction`, or `messages[].role` in `["system", "developer"]`), tool contract, tool history, or freshness-sensitive state
- **THEN** `SemanticCacheManager` SHALL partition Layer-2 cache keys by `ct:<sha256_16>`, `tc:<sha256_16>`, and `sp:<sha256_16>` so an incompatible cached response is never reused across different system policies or tool contracts while identical system-policy repeats hit Layer-2.

#### Scenario: Shared Redis reaches its proposed memory budget
- **WHEN** a candidate eviction policy is evaluated against a Redis instance shared by cache and coordination consumers
- **THEN** the report SHALL identify which keys can be lost and whether enforcement weakens, and SHALL NOT assume that all expiring keys are disposable cache data or that maxmemory equals total process memory.

### Requirement: Gemini 4 Carbon Tier Combos and SQLite Capability Overrides Without Source Modifications
OmniRoute SHALL expose four top-level Google Gemini 4 Carbon combos (`gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low`) routed via `strategy: "quota-weighted"` across the three entitled Google AI Ultra `agy` connections and SHALL persist SQLite capability and context overrides (`1,048,576` context, `262,144` max output tokens, `["low", "medium", "high"]` efforts) without modifying git-tracked source code.

#### Scenario: SQLite capability and context overrides unlock 262,144 output tokens and 1M context for Carbon tiers
- **WHEN** 12 single-key `PATCH http://127.0.0.1:20128/api/model-capability-overrides` requests (`3 models × 4 keys`, passing `"low,medium,high"` as a comma-separated string for `reasoning_efforts`) are applied and `GET /api/model-capability-overrides` + `GET /v1/models` are queried
- **THEN** `antigravity/gemini-4-carbon-high`, `antigravity/gemini-4-carbon-medium`, and `antigravity/gemini-4-carbon-low` SHALL each report persisted overrides for `context_length: 1048576`, `max_input_tokens: 1048576`, `max_output_tokens: 262144`, and `reasoning_efforts: ["low", "medium", "high"]`
- **AND** top-level combos `gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` in `/v1/models` (`owned_by: "combo"`) SHALL advertise `context_length: 1000000` and `max_output_tokens: 262144` without rejecting requests carrying `max_tokens > 65536` up to `262144`

#### Scenario: Four Gemini 4 Carbon combos route exclusively across the three Ultra Antigravity accounts via quota-weighted strategy
- **WHEN** `GET http://127.0.0.1:20128/api/combos` is queried
- **THEN** combos `gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` SHALL each be active with `strategy: "quota-weighted"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.quotaWeightedFloorPercent: 5`, `config.quotaWeightedScoring: "leftover"`, `config.resetAwareQuotaCacheTtlMs: 300000`, `config.resetWindowQuotaCacheTtlMs: 300000`, and `config.resetAwareQuotaCacheMaxStaleMs: 3600000`
- **AND** `gemini-4-carbon` and `gemini-4-carbon-high` SHALL each contain exactly 3 `kind: "model"` steps with `model: "agy/gemini-4-carbon-high"` pinned to `0532bad4-2486-4286-8f06-510e9c678620` (`vinhvumobile@gmail.com`), `338764b8-1cd7-4946-b789-ee5dad4c5073` (`vinhghtk1908@gmail.com`), and `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`vicgnome19094@gmail.com`), while `gemini-4-carbon-medium` and `gemini-4-carbon-low` SHALL map those same 3 Ultra connections to `agy/gemini-4-carbon-medium` and `agy/gemini-4-carbon-low` respectively
- **AND** zero non-Ultra (`g1-pro-tier`) `connectionId` values SHALL appear in any `gemini-4-carbon*` combo

#### Scenario: Concurrent Carbon inference distributes load by remaining quota and in-flight count
- **WHEN** concurrent `POST /v1/chat/completions` or `POST /v1/responses` requests target `gemini-4-carbon` or `gemini-4-carbon-high`
- **THEN** OmniRoute SHALL weight candidate selection by `score / (1 + inflight)` across the 3 Ultra accounts, reserve `inflight` synchronously in the same event-loop turn before yielding, and return `HTTP 200` completions with zero `429` dispatches to unentitled Pro accounts

### Requirement: Quota-Weighted Concurrency Balancing, Ultra Pool Isolation, and Rate-Limit Queue Scaling Across Antigravity Combos
OmniRoute SHALL configure multi-account Antigravity (`agy`) combos (`gemini-4-argon*`, `gemini-3.8-flash-high`, `claude-opus-5.5`, `claude-sonnet-5.5`) with `strategy: "quota-weighted"`, isolate `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5` to the 11 active Pro `agy` accounts, disable `rateLimitProtection` on active `agy` connections, and scale `settings.requestQueue` to 64 concurrent requests.

#### Scenario: Argon combos prune unentitled Pro accounts and balance across the 3 Ultra accounts via quota-weighted routing
- **WHEN** `GET /api/combos` is queried for `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low`
- **THEN** each combo SHALL have `strategy: "quota-weighted"`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.quotaWeightedFloorPercent: 5`, and exactly 3 `kind: "model"` steps pinned to the 3 Ultra `agy` accounts (`0532bad4`, `338764b8`, `62af823b`), with all 7 exhausted/unentitled Pro `agy` steps removed

#### Scenario: `gemini-3.8-flash-high` routes exclusively across the 11 active Pro accounts without Ultra quota bleed
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is queried or invoked under concurrent subagent load
- **THEN** `strategy` SHALL be `"quota-weighted"`, `config.targetTimeoutMs` SHALL be `120000`, `config.predictiveTtftMs` SHALL be `0`, and `models` SHALL contain 11 `agy/gemini-3.8-flash-high` steps pinned to the 11 active Google AI Pro `agy` connections (`38782750`, `9d66311f`, `ce95e1cb`, `9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`)
- **AND** none of the 3 Ultra `agy` accounts (`62af823b`, `0532bad4`, `338764b8`) SHALL appear in `gemini-3.8-flash-high`, preserving Ultra weekly quota exclusively for `gemini-4-argon*` and `gemini-4-carbon*`

#### Scenario: `claude-opus-5.5` and `claude-sonnet-5.5` route exclusively across the 11 active Pro Antigravity accounts with native 5.5 tiers on the 9 entitled accounts
- **WHEN** `GET /api/combos` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** both combos SHALL configure `strategy: "quota-weighted"`, `context_length: 1000000`, `context_cache_protection: false`, `config.quotaWeightedFloorPercent: 1`, and 11 `kind: "model"` steps covering the 11 active Google AI Pro `agy` connections (excluding the 3 Ultra accounts `0532bad4`, `338764b8`, and `62af823b` so Claude usage cannot trigger `genericQuotaFetcher.ts`'s unscoped `argon` family quota aggregation)
- **AND** the 9 Pro connections advertising native 5.5 in `syncedAvailableModels` (`38782750`, `9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`) SHALL use `agy/claude-opus-5-5-high` and `agy/claude-sonnet-5-5-high`, while the remaining 2 active Pro connections (`9d66311f`, `ce95e1cb`) SHALL use `agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6`

#### Scenario: All 14 active Antigravity connections disable local rateLimitProtection and requestQueue scales to 64 concurrent requests
- **WHEN** `provider_connections` (`provider = 'agy' AND is_active = 1`) and `GET /api/settings` are inspected
- **THEN** all 14 active `agy` connections SHALL have `rate_limit_protection = 0` (`rateLimitProtection: false`) so individual connections are not locally serialized at 20 concurrent requests
- **AND** `settings.requestQueue` SHALL be configured with `concurrentRequests: 64`, `requestsPerMinute: 600`, and `maxWaitMs: 15000`, while `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` and `COMBO_AUTO_PRUNE_STALE_STEPS` remain `"false"` in `feature_flags`
