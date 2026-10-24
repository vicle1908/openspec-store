# Proposal

## Why

OmniRoute (`v3.8.52`) currently injects up to 7,026 tokens of stale regex-scraped and AgentMemory-consolidation rows into every authenticated chat call (`memoryEnabled: true`, `skillsEnabled: true` with 285,844 cumulative row accesses), silently truncates prior-turn tool results at 2,000 characters via `lite.compressToolResults: true`, omits `codex-responses` (`/v1/responses` `function_call_output` compression) and an explicit `ladderOverride` on `contextBudget`, and leaves four zero-restart resilience flags plus `claudeClassifierCompat: "auto"`, `claudeFastMode`, `maxBodySizeMb: 50`, and `models.dev` capability sync unconfigured. Disabling the duplicate built-in memory scraper, preserving prior-turn `Read`/`Grep` tool results under `lite`, configuring `codex-responses` with a prose-safe `ladderOverride`, and enabling the verified resilience flags and classifier short-circuit eliminates ~7K tokens/turn of prompt bleed and prevents silent 2 KB tool truncation across coding agents.

## What Changes

- **Disable Built-in Memory & Skills and Purge 75 Stale Rows**:
  - Set `enabled: false`, `skillsEnabled: false`, and `maxTokens: 0` via `PUT http://127.0.0.1:20128/api/settings/memory` (matching upstream v3.8.30+ defaults and delegating all memory operations to the workstation's dedicated AgentMemory MCP service).
  - Iterate `DELETE http://127.0.0.1:20128/api/memory/{id}` over all 75 rows returned by `GET /api/memory?limit=100` to clear the 7,026 tokens from `memories`, `memory_fts`, `sqlite-vec`, and `_memoryCache`.
- **Prevent 2 KB `lite` Tool Truncation, Enable `codex-responses`, and Set Prose-Safe `ladderOverride`**:
  - Set `lite: {"compressToolResults": false, "maxToolLength": 200000}` in `/api/settings/compression` so `SAFE_DEFAULT_PIPELINE` (`session-dedup` + `lite`) stops truncating prior-turn `Read`/`Grep`/tool outputs at 2,000 characters (`open-sse/services/compression/lite.ts:23,305`).
  - Enable `engines["headroom"]: {"enabled": true}`, `engines["codex-responses"]: {"enabled": true}`, and `codexResponsesConfig: {"enabled": true, "minBytes": 512, "maxLines": 160, "preserveToolNames": ["Read", "Glob", "Grep", "Write", "Edit", "WebSearch", "WebFetch", "read", "glob", "grep", "write", "edit", "web_search", "web_fetch", "find"]}` so normal headerless turns include lossless `headroom` (`lossy: false`) alongside `session-dedup` and `lite`, and `/v1/responses` `function_call_output` compression is configured.
  - Set `contextBudget.ladderOverride` (`[{"engine": "session-dedup"}, {"engine": "headroom"}, {"engine": "lite"}, {"engine": "codex-responses"}, {"engine": "rtk", "intensity": "minimal"}]`) under `mode: "replace-autotrigger"` and `policy: "percentage"` (`pct: 0.85`). Document the `v3.8.52` runtime interaction: when `config.engines` has enabled engines (`basePlan.mode === "stacked"`, `baseRank = 50 > 0`), headerless requests run the lossless `[session-dedup, lite, headroom]` pipeline (`resolveAdaptivePlan.ts:48-54`) and reactive `compressContext` at 70% window capacity, while requests carrying `x-omniroute-compression: allow-lossy` (or `engine:codex-responses` / `engine:rtk`) execute `codex-responses` and `rtk` directly.
- **Enable 4 Verified Zero-Restart Resilience Feature Flags**:
  - Enable via individual `PUT /api/settings/feature-flags` calls (`{"key": "<FLAG>", "value": "true"}`):
    1. `QUOTA_WINDOW_BOUNDED_PARK` (`src/domain/quotaCache.ts:970` — releases stale cached 5h/weekly quota parks after `EXHAUSTED_MAX_PARK_MS`).
    2. `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED` (`src/sse/handlers/chat.ts:1809,2385` — 1 sibling connection failover on pre-first-frame `STREAM_EARLY_EOF`).
    3. `COOLDOWN_RETRY_SKIP_REFUSALS_ENABLED` (`src/sse/services/cooldownAwareRetry.ts:25,164` — skips cooldown wait on `403`/`410` refusals).
    4. `PROVIDER_SAFETY_STOPS_TERMINAL` (`open-sse/services/combo.ts:681,805` — stops combo retry loops on terminal `content_policy_violation` / `misalignment_policy_violation`).
  - Explicitly keep `FLUSH_EMPTY_RETRY_ENABLED=false` (avoids buffering 256 KB before emitting first SSE byte on translated streams), `ADAPTIVE_ADMISSION_MODE=shadow`, `taskRouting.enabled=false`, `backgroundDegradation.enabled=false`, `engines.ccr.enabled=false`, and `PII_REDACTION_ENABLED=false`.
- **Global Settings (`claudeClassifierCompat`, `claudeFastMode`, `maxBodySizeMb`) & `models.dev` Sync**:
  - Update `PATCH /api/settings` with `claudeClassifierCompat: "auto"`, `claudeFastMode: {"enabled": true, "supportedModels": ["claude-fable-5", "claude-opus-5-5", "claude-opus-5", "claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6"]}`, `maxBodySizeMb: 50`, and `modelsDevSyncEnabled: true`.
  - Trigger `POST /api/settings/models-dev` with `{"action": "sync"}` (synchronous capability + pricing hydration) followed by `{"action": "start"}` (24h periodic timer) so `GET /api/settings/models-dev?action=status` deterministically reports `enabled: true` and `lastSync !== null`.
  - Note: should `omniroute` container exhibit any entrypoint bind-mount issue (`container-entrypoint-compat.sh`), verify container mount health before executing API updates.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `omniroute-compression-and-routing`: Adds normative requirements for disabling built-in memory/skill prompt injection, disabling `lite.compressToolResults` 2 KB truncation, enabling `codex-responses` with a prose-safe `contextBudget.ladderOverride`, enabling the 4 additional resilience feature flags, and configuring `claudeClassifierCompat: "auto"`, `claudeFastMode`, `maxBodySizeMb: 50`, and `models.dev` sync.

## Non-Goals

- Enabling `FLUSH_EMPTY_RETRY_ENABLED` (which buffers up to 256 KB of translated SSE streams before emitting the first byte).
- Switching `ADAPTIVE_ADMISSION_MODE` from `shadow` to `enforce` (which rejects >60% of high-tool-count coding turns at default `initialLimit: 64`).
- Enabling `taskRouting`, `backgroundDegradation`, `ccr`, `PII_REDACTION_ENABLED`, or OmniRoute's internal MCP/A2A servers.
- Modifying tracked files in `/Users/androidteam/Omniroute`.

## Ownership Boundaries

- **Affected System**: OmniRoute AI gateway runtime (`http://127.0.0.1:20128`), user-level skills (`~/.agents/skills/`), and workspace docs/wiki (`~/Developer/docs/`, `~/Developer/wiki/`).
- **Owner**: AI Platform Engineering / Workstation tooling.
- **Client Consumers**: Claude Code, Codex CLI, OMP (Oh My Pi), Goose CLI, Grok Build, Muse Code.

## Impact

- **Token & Latency Savings**: Eliminates up to 7,026 tokens of stale `Memory context:` injection on every authenticated `/v1/chat/completions` and `/v1/messages` turn; short-circuits Claude Code `--permission-mode auto` security classifier sub-requests in `<1ms`.
- **Correctness & Reliability**: Stops `lite` from silently truncating prior-turn file reads (`Read`/`Grep`) at 2,000 chars; enables tool-aware `/v1/responses` output compression (`codex-responses`); prevents combo retry storms on content-policy stops and 403/410 refusals.
- **Breaking Changes**: None.
