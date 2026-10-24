# Spec Delta

## ADDED Requirements

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
