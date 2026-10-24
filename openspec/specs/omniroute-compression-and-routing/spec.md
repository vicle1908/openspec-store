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
