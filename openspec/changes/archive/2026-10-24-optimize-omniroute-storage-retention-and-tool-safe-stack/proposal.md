# Proposal

## Why

The OmniRoute (`v3.8.52`) named volume (`omniroute-data`) has grown to 2.88 GB (`1.38 GB` in `/app/data/call_logs/` across 10,000 JSON files and `693 MB` in `/app/data/storage.sqlite` due to 365-day `usage_history` and 7-day `conversation_turn_nodes` retention), headerless coding clients still miss automatic `rtk` and `codex-responses` tool-output compression because `config.compressionComboId` is unset and `caveman` (`lossy: true`) is enabled in `engines`, and slow or permanently banned OAuth seats (`vicgnome19096@gmail.com` at 73.4s average latency and `11%` success rate) are not skipped by the Predictive TTFT Circuit Breaker (`zeroLatencyOptimizationsEnabled: false`) or auto-disabled on permanent bans (`autoDisableBannedAccounts: false`). Tuning database/log retention and call-log artifact caps, configuring the server-side tool-safe `default-caveman` compression combo (`caveman` disabled, `rtk` + `codex-responses` active across all headerless turns), and enabling the Predictive TTFT Circuit Breaker (`predictiveTtftMs: 25000`, `hedging: false`) and subscription ban auto-disable reclaims ~1.5+ GB of storage and activates automatic tool-output compression and slow-target protection across all coding clients.

## What Changes

- **Database Retention, Aggregation & Call-Log Artifact Caps**:
  - Update `PATCH http://127.0.0.1:20128/api/settings/database` with `retention: {"conversationTurnNodes": 2, "usageHistory": 30, "quotaSnapshots": 3, "callLogs": 7, "compressionAnalytics": 7, "compressionCacheStats": 7, "xpAuditLog": 7, "domainCostHistory": 14, "autoCleanupEnabled": true}`, `aggregation: {"enabled": true, "rawDataRetentionDays": 7}`, and `backup: {"autoBackupEnabled": true, "autoBackupFrequency": "daily", "keepLastNBackups": 2}`.
  - Add `- CALL_LOG_MAX_ENTRIES=2000`, `- CHAT_LOG_MAX_BODY_KB=256`, `- CALL_LOGS_TABLE_MAX_ROWS=25000`, and `- PROXY_LOGS_TABLE_MAX_ROWS=25000` to `/Users/androidteam/Omniroute/docker-compose.override.yml` so `rotateCallLogs()` caps `/app/data/call_logs/` at 2,000 artifacts (~200 MB instead of 1.38 GB).
- **Server-Side Tool-Safe Compression Stack (`caveman: false` + `compressionComboId: "default-caveman"`)**:
  - Update `PUT http://127.0.0.1:20128/api/context/combos/default-caveman` to set `pipeline: [{"engine": "session-dedup"}, {"engine": "lite"}, {"engine": "rtk", "intensity": "minimal"}, {"engine": "codex-responses"}, {"engine": "headroom"}]`, `outputMode: false`, and `isDefault: true`.
  - Update `PUT http://127.0.0.1:20128/api/settings/compression` to set `engines.caveman: {"enabled": false, "level": "lite"}`, `cavemanConfig: {"enabled": false, "intensity": "lite"}`, `compressionComboId: "default-caveman"`, and `stackedPipeline: [{"engine": "session-dedup"}, {"engine": "lite"}, {"engine": "rtk", "intensity": "minimal"}, {"engine": "codex-responses"}, {"engine": "headroom"}]` so `chatCore.ts:1512-1522` (`!config.compressionComboId === false`) executes the 5-step tool-safe pipeline automatically on **all headerless requests** while keeping user/assistant prose 100% unmodified and `Read`/`Grep`/`Glob`/`Edit`/`Write` protected.
- **Predictive TTFT Circuit Breaker, Unleased 2-Account Pool Concurrency & Auto-Disable Banned Subscription Accounts**:
  - Update `PATCH http://127.0.0.1:20128/api/settings/combo-defaults` to set `comboDefaults.zeroLatencyOptimizationsEnabled: true`, `predictiveTtftMs: 25000` (25s), `hedging: false` (no duplicate token spend), and `fallbackCompressionMode: "off"` (avoiding `executeTargetAttempt.ts:267-275`'s unconfigured `applyCompression` call that would re-enable `lite.compressToolResults = true`), and update the `agy` combos (`gemini-3.8-flash-high`, `gemini-4-argon{,-high,-medium,-low}`, `claude-opus-5.5`, `muse-spark-1.3`) so `config.zeroLatencyOptimizationsEnabled` is `true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`).
  - Set `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED: "false"` via `PUT http://127.0.0.1:20128/api/settings/feature-flags` so 2-account `gemini-4-argon*` pools allow concurrent subagent/tool-loop streams on the same account without `503 All eligible Antigravity accounts are currently handling a request for this model` rejections, and update `PUT http://127.0.0.1:20128/api/settings/auto-disable-accounts` with `{"enabled": true, "scope": "subscription", "threshold": 3}` so permanently banned OAuth/subscription accounts are automatically deactivated (`banDisabledAt`) while prepaid API keys remain protected.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `omniroute-compression-and-routing`: Adds normative requirements for database/call-log retention bounds, server-side tool-safe stacked compression (`caveman: false`, `compressionComboId: "default-caveman"`), Predictive TTFT Circuit Breaker (`zeroLatencyOptimizationsEnabled: true`, `predictiveTtftMs: 25000`, `hedging: false`), and subscription-scoped permanent-ban auto-deactivation.

## Non-Goals

- Enabling speculative request hedging (`hedging: true`), which duplicates upstream token spend across parallel targets.
- Setting `autoDisableBannedScope: "all"` (which could disable prepaid API key connections on transient upstream errors).
- Modifying tracked files in `/Users/androidteam/Omniroute`.

## Ownership Boundaries

- **Affected System**: OmniRoute AI gateway runtime (`http://127.0.0.1:20128` and `20129`, untracked `~/Omniroute/docker-compose.override.yml`), user-level skills (`~/.agents/skills/`), and workspace wiki (`~/Developer/wiki/`).
- **Owner**: AI Platform Engineering / Workstation tooling.
- **Client Consumers**: Claude Code, Codex CLI, OMP (Oh My Pi), Goose CLI, Grok Build, Muse Code.

## Impact

- **Storage Reclamation**: Shrinks `/app/data/call_logs/` from `1.38 GB` (10,000 files) to `~200 MB` (2,000 files, 256 KB max body) and `/app/data/storage.sqlite` from `693 MB` to `~200–240 MB` via incremental vacuum, saving **>1.5 GB** on the host disk.
- **Automatic Tool Compression**: Headerless coding clients (OMP, Claude Code, Codex, Goose, Muse) automatically run `[session-dedup, lite, rtk (minimal), codex-responses, headroom]` on every turn without prose modification (`caveman: false`).
- **Tail-Latency & Ban Protection**: Attempt-0 targets with historical average latency >25s (such as `vicgnome19096@gmail.com` at 73.4s) are skipped immediately by the Predictive TTFT Circuit Breaker, and permanently banned OAuth seats are automatically quarantined.
- **Breaking Changes**: None.
