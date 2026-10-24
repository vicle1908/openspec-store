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

OmniRoute SHALL configure `memoryEnabled: false`, `skillsEnabled: false`, and `memoryMaxTokens: 0` via `/api/settings/memory` and SHALL retain zero stored entries in its internal `memories` table so authenticated chat requests do not inject duplicate `Memory context:` blocks or scrape regex fragments from coding agent and AgentMemory consolidation traffic.

#### Scenario: Authenticated chat request bypasses built-in memory injection and extraction
- **WHEN** an authenticated client submits a request to `/v1/chat/completions`, `/v1/messages`, or `/v1/responses`
- **THEN** OmniRoute SHALL neither prepend `Memory context:` nor inject `memory_*` tools nor run post-response regex fact extraction into the `memories` table

#### Scenario: Internal memory store remains empty
- **WHEN** `GET /api/memory?limit=1` is queried
- **THEN** OmniRoute SHALL return `total: 0` and `stats.tokensUsed: 0`

### Requirement: Lossless `lite` Tool Result Preservation, `codex-responses` Engine, and Prose-Safe Context Budget Ladder

OmniRoute SHALL configure `lite.compressToolResults` as `false` (`maxToolLength: 200000`), SHALL enable `headroom` (`engines.headroom.enabled: true`) and `codex-responses` (`codexResponsesConfig.enabled: true`), and SHALL set `contextBudget` (`mode: "replace-autotrigger"`, `policy: "percentage"`, `pct: 0.85`) with `ladderOverride` ordered as `session-dedup`, `headroom`, `lite`, `codex-responses`, and `rtk` (`minimal`).

#### Scenario: Headerless multi-turn requests preserve prior-turn `Read` and `Grep` tool results under `[session-dedup, lite, headroom]`
- **WHEN** a coding client submits a multi-turn request without an `x-omniroute-compression` header and with prior-turn tool results exceeding 2,000 characters
- **THEN** OmniRoute SHALL run its lossless `[session-dedup, lite, headroom]` pipeline and `lite` SHALL NOT truncate prior-turn tool results to 2,000 characters (`compressToolResults: false`)

#### Scenario: Lossy-opt-in and `codex-responses` requests compress `/v1/responses` and `/v1/chat/completions` tool outputs while protecting file reads
- **WHEN** a request opts into lossy compression (`x-omniroute-compression: allow-lossy`, `engine:codex-responses`, or `engine:rtk`) or invokes `ladderOverride` (`basePlan.mode === "off"` at >85% `percentage` context budget)
- **THEN** OmniRoute SHALL execute `codex-responses` (on `/v1/responses` `function_call_output` items, protecting `Read`, `Glob`, `Grep`, `Write`, `Edit`, `WebSearch`, `WebFetch`, `find`) and `rtk` (`minimal` intensity on tool results)

### Requirement: Bounded Quota Park, Early-EOF Sibling Failover, Refusal Cooldown Skip, and Terminal Safety Stops

OmniRoute SHALL enable the feature flags `QUOTA_WINDOW_BOUNDED_PARK`, `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED`, `COOLDOWN_RETRY_SKIP_REFUSALS_ENABLED`, and `PROVIDER_SAFETY_STOPS_TERMINAL` via string-valued (`"true"`) database overrides while keeping `FLUSH_EMPTY_RETRY_ENABLED` disabled (`"false"`) to preserve unbuffered streaming TTFT.

#### Scenario: Pre-first-frame SSE early EOF fails over once to a sibling connection
- **WHEN** `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED` is `true` and an upstream SSE stream closes with `STREAM_EARLY_EOF` before emitting any useful frame
- **THEN** OmniRoute SHALL exclude the failed connection and retry once on an eligible sibling connection

#### Scenario: Content-policy safety refusal stops combo retry loop
- **WHEN** `PROVIDER_SAFETY_STOPS_TERMINAL` is `true` and an upstream target returns HTTP 400 or 403 with `content_policy_violation` or `misalignment_policy_violation`
- **THEN** OmniRoute SHALL treat the refusal as terminal for the request and SHALL NOT retry the refused prompt across remaining combo targets

### Requirement: Claude Classifier Short-Circuit, Fast Mode Opus 5.5 Support, 50 MB Body Limit, and `models.dev` Capability Sync

OmniRoute SHALL configure `claudeClassifierCompat: "auto"`, include `"claude-opus-5-5"` in `claudeFastMode.supportedModels`, set `maxBodySizeMb: 50`, and enable periodic `models.dev` capability sync (`modelsDevSyncEnabled: true`, `action: "start"`).

#### Scenario: Claude Code auto-mode security classifier short-circuited locally
- **WHEN** `claudeClassifierCompat` is `"auto"` and Claude Code sends an Anthropic Messages request whose system prompt contains `"You are a security monitor for autonomous AI coding agents"`
- **THEN** OmniRoute SHALL immediately return a synthetic HTTP 200 default-allow response (`<block>no</block>` or `<severity>0</severity>`) without dispatching an upstream LLM request

### Requirement: Bounded SQLite Table Retention, Usage Rollup Aggregation, and Call-Log Artifact Caps

OmniRoute SHALL configure bounded database retention (`conversationTurnNodes: 2`, `usageHistory: 30`, `quotaSnapshots: 3`, `callLogs: 7`, `compressionAnalytics: 7`, `compressionCacheStats: 7`, `xpAuditLog: 7`, `domainCostHistory: 14`), enable `aggregation` (`enabled: true`), limit daily DB backups (`keepLastNBackups: 2`), and cap call-log artifacts (`CALL_LOG_MAX_ENTRIES=2000`, `CHAT_LOG_MAX_BODY_KB=256`).

#### Scenario: Usage history rollup and bounded table retention on auto-cleanup
- **WHEN** the 6-hourly `runAutoCleanup()` pass executes with `aggregation.enabled: true` and `retention.usageHistory: 30`
- **THEN** OmniRoute SHALL roll up `usage_history` rows older than 30 days into `daily_usage_summary` before deleting them, prune `conversation_turn_nodes` older than 2 days and `quota_snapshots` older than 3 days, and reclaim freed SQLite pages via bounded `PRAGMA incremental_vacuum`

#### Scenario: Call-log artifact volume bounded on disk
- **WHEN** `CALL_LOG_MAX_ENTRIES=2000` and `CHAT_LOG_MAX_BODY_KB=256` are configured in `docker-compose.override.yml`
- **THEN** `rotateCallLogs()` SHALL cap `/app/data/call_logs/` at 2,000 JSON files with bodies truncated at 256 KB

### Requirement: Server-Side Tool-Safe Default Compression Stack Without Prose Modification

OmniRoute SHALL disable `caveman` (`engines.caveman.enabled: false`, `cavemanConfig.enabled: false`) and SHALL configure `compressionComboId: "default-caveman"` with `stackedPipeline` ordered as `session-dedup`, `lite` (`compressToolResults: false`), `rtk` (`intensity: "minimal"`), `codex-responses`, and `headroom` so headerless coding requests execute tool-output compression automatically without modifying user or assistant prose.

#### Scenario: Headerless coding request executes `rtk` and `codex-responses` without prose mutation
- **WHEN** a coding client submits a multi-turn request without an `x-omniroute-compression` header containing verbose shell/test tool outputs and `Read`/`Grep` file outputs
- **THEN** OmniRoute (`config.compressionComboId === "default-caveman"`) SHALL execute `[session-dedup, lite, rtk, codex-responses, headroom]` to compress the shell/test tool outputs while preserving user/assistant prose (`caveman: false`) and `Read`/`Grep`/`Glob`/`Edit`/`Write` file outputs verbatim

### Requirement: Predictive TTFT Circuit Breaker, Unleased 2-Account Pool Concurrency, and Subscription-Scoped Ban Auto-Disable

OmniRoute SHALL enable `zeroLatencyOptimizationsEnabled: true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) in `/api/settings/combo-defaults` and `agy` combos, set `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` to `"false"`, and configure `/api/settings/auto-disable-accounts` (`enabled: true`, `scope: "subscription"`, `threshold: 3`).

#### Scenario: Stalled target exceeding 25-second average latency skipped on attempt 0 without fallback re-truncation
- **WHEN** `zeroLatencyOptimizationsEnabled` is `true` (`predictiveTtftMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) and a target's historical `avgLatencyMs` in `getComboMetrics` exceeds 25,000 milliseconds
- **THEN** OmniRoute SHALL skip that target on primary attempt `0` (`predictive_ttft`) and dispatch to the next healthy candidate without issuing duplicate speculative hedged requests or running unconfigured fallback `lite` truncation

#### Scenario: Concurrent subagent streams on 2-account `gemini-4-argon` pool proceed without lease saturation 503
- **WHEN** `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` is `"false"` and more than two concurrent streaming requests target `gemini-4-argon*`
- **THEN** OmniRoute SHALL allow concurrent streams on the two entitled `Ultra` `agy` accounts without returning `503 All eligible Antigravity accounts are currently handling a request for this model`

#### Scenario: Permanently banned OAuth subscription account automatically quarantined
- **WHEN** an OAuth/subscription connection (`agy`, `github`, `muse-code`) receives a permanent ban classification (`permanent: true`) while `auto-disable-accounts` is enabled with `scope: "subscription"`
- **THEN** OmniRoute SHALL set `isActive: false` and stamp `banDisabledAt` on that connection while leaving `apikey`-authenticated connections unaffected
