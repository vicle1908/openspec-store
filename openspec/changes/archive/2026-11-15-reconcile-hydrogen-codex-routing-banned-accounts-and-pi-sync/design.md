# Design

## Context

See `proposal.md` for motivation and official-doc findings (`openai/codex` `codex-rs/core/src/session/mod.rs` + `codex-rs/codex-api/src/sse/responses.rs`, OpenAI Responses API streaming reference, `~/Omniroute` `open-sse/services/combo/{strategyRegistry,quotaStrategies}.ts` + `src/app/api/v1/responses/route.ts`, and `@earendil-works/pi-coding-agent` `1.5.2` `CHANGELOG.md` + `settings-manager.js`).

Key existing patterns in OmniRoute and host automation:
- **Multi-account combo load distribution (`open-sse/services/combo/quotaStrategies.ts:854-947`)**: `gemini-3.8-flash-high`, `gemini-4-argon*`, and `gemini-4-carbon*` already use `strategy: "quota-weighted"` with `config.predictiveTtftMs: 0` so `orderTargetsByQuotaWeighted` + synchronous `incrementInflight` distributes concurrent sessions across active accounts instead of piling onto `targets[0]`.
- **Single-writer SQLite transactions**: `~/.omp/agent/agent.db` runs WAL mode and uses `BEGIN IMMEDIATE; ... COMMIT;` for OAuth credential pruning (`auth_credentials`), while OmniRoute `/app/data/storage.sqlite` combo mutations use the authenticated HTTP API `PUT /api/combos/{id}` (automatically validating combo schemas and updating in-memory/SQLite state without restarting the container).
- **Atomic host config updates & backups**: Pre-mutation backups (`chmod 600`) + SHA-256 manifests live under `~/.omniroute/backups/<change-name>/` (`chmod 700`), and JSON/TOML configs are mutated atomically via temp-file + `os.replace` preserving `0600` mode.

## Goals / Non-Goals

**Goals:**
- Eliminate all remaining references to banned `62af823b` (`vicgnome19094@gmail.com`) across OmniRoute combos (`gemini-4-argon*`, `gemini-4-carbon*`) and OMP `agent.db` (`id = 3`).
- Eliminate single-account `targets[0]` burst saturation on `gemini-4-hydrogen*` by switching all 5 Hydrogen combos (`gemini-4-hydrogen{,-xhigh,-high,-medium,-low}`) to `quota-weighted` with `predictiveTtftMs: 0`, `quotaWeightedFloorPercent: 5`, and `quotaWeightedScoring: "leftover"` (`gemini-4-hydrogen` stays flattened `nestedComboMode` unset/`"flatten"` so flattened targets inherit `quota-weighted` ordering).
- Align `~/.codex/config.toml` with `openai/codex` official schema by removing unsupported `service_tier = "ultrafast"` and validate zero `unsupported_service_tier_warning` diagnostics plus protocol-level `/v1/responses` completion over `quota-weighted` `gemini-4-hydrogen`.
- Align `~/.pi/agent/settings.json` (`lastChangelogVersion: "1.5.2"`), `wiki/entities/pi.md`, `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md`, and Notion with live Pi `1.5.2` (`N-1` `1.5.1` retention).
- Refresh `openspec-store` GitNexus index safely without altering another session's uncommitted files.

**Non-Goals:**
- No edits to `~/Omniroute` container source or `RESPONSES_TRANSPORT_KEEPALIVE_ENABLED` / `DEFAULT_THRESHOLD_MS` flags.
- No edits to `~/.pi/agent/models.json`, `~/.omp/agent/models.yml`, or OMP `modelRoles`.
- No edits to `scripts/knowledge-refresh/refresh-knowledge-indexes.sh`, `scripts/workstation-daily-update.sh`, `openspec/changes/standardize-uv-script-execution-and-toolchain-resilience/`, or `wiki/entities/tailscale.md`.

## Decisions

### 1. Switch `gemini-4-hydrogen-{xhigh,high,medium,low}` Combos from `priority` to `quota-weighted`
- **Choice**: Update `gemini-4-hydrogen`, `gemini-4-hydrogen-xhigh`, `gemini-4-hydrogen-high`, `gemini-4-hydrogen-medium`, and `gemini-4-hydrogen-low` via `PUT http://127.0.0.1:20128/api/combos/{id}` to `strategy: "quota-weighted"` with `predictiveTtftMs: 0`, `quotaWeightedFloorPercent: 5`, `quotaWeightedScoring: "leftover"`, `failoverBeforeRetry: true`, `retryDelayMs: 500`, `targetTimeoutMs: 180000`, `candidatePool: ["agy"]`, and the 5 active WTU-Pro connections `[9c033d6f, 37f9924d, 573e3f41, 3f3085b1, a94216f4]`. Keep top-level `gemini-4-hydrogen` flattened (`nestedComboMode` unset/`"flatten"`) rather than `nestedComboMode: "execute"` because `tryRuntimeUnitDispatch` only runs in `"execute"` mode (whereas flattened execution runs `applyStrategyOrdering(combo.strategy)` on the parent combo's strategy).
- **Rationale**: Under `priority`, `strategyRegistry.ts` uses `ordering: "declared"`, forcing every concurrent OMP/Codex/CLI request onto `9c033d6f` first, exhausting its Antigravity burst/TPM budget and triggering `AG_429_BUDGET` (`2`) + `rememberAntigravity429Refusal` lockouts. When HTTP `200` SSE headers are already flushed at `DEFAULT_THRESHOLD_MS = 1000` ms, subsequent `429`s become mid-stream `rate_limit_exceeded` frames that Codex treats as stream disconnects (`95s+` retry backoff). `quota-weighted` with a `5%` floor spreads load across all 5 active WTU-Pro accounts immediately and matches `gemini-3.8-flash-high`, `gemini-4-argon*`, and `gemini-4-carbon*`.
- **Alternative rejected**: Enabling `RESPONSES_TRANSPORT_KEEPALIVE_ENABLED=true` in OmniRoute. Official `openai/codex` `codex_api::sse::responses` confirmed blank-line `\n\n` frames do not reset `stream_idle_timeout` (`300s`), and keeping `DEFAULT_THRESHOLD_MS = 1000` ms avoids modifying upstream container env/code.

### 2. Prune `62af823b` (`vicgnome19094@gmail.com`) via API + Single-Transaction SQLite
- **Choice**: Remove `62af823b` from `gemini-4-argon{,-high,-medium,-low}` and `gemini-4-carbon{,-high,-medium,-low}` via `PUT /api/combos/{id}` (leaving `[0532bad4, 338764b8]`), and delete `id = 3` (`vicgnome19094@gmail.com`) from `~/.omp/agent/agent.db` inside `BEGIN IMMEDIATE; DELETE FROM auth_credentials WHERE id = 3 AND provider = 'google-antigravity'; COMMIT;`.
- **Transaction boundary**: Capture an OmniRoute SQLite snapshot (`PUT /api/db-backups` or `docker exec` + `sqlite3` backup) + `~/.omp/agent/agent.db.bak` (`0600`) with `PRAGMA quick_check = ok` before mutating either store. Leave `provider_connections` row `62af823b` in OmniRoute with `is_active = 0, test_status = 'banned'` so `findExistingAgyConnection` blocks accidental re-import.

### 3. Omit `service_tier = "ultrafast"` in `~/.codex/config.toml`
- **Choice**: Delete line `service_tier = "ultrafast"` from `~/.codex/config.toml` (leaving `service_tier` unset) while keeping `model = "gemini-4-hydrogen"`, `model_reasoning_effort = "high"`, and default `stream_idle_timeout_ms` (`300,000` ms).
- **Rationale**: `openai/codex` `codex-rs/core/src/session/mod.rs` only passes `service_tier` without warning when the target catalog entry explicitly advertises support; omitting `service_tier` eliminates `unsupported_service_tier_warning` without overriding model-catalog defaults (whereas `"default"` suppresses catalog defaults).

### 4. Align Pi `1.5.2` Settings, Specs, Wiki, Skill, and Notion
- **Choice**: Set `"lastChangelogVersion": "1.5.2"` in `~/.pi/agent/settings.json` (`0600`), document active `1.5.2` + `N-1` `1.5.1` retention in `pi-agent-harness-config/spec.md`, update `wiki/entities/pi.md` and `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` to `1.5.2`, and run `sync-notion-knowledge.sh --section entities` + AgentMemory remember/mesh sync.
- **Alternative rejected**: Deleting `1.5.1/` to force single-release retention. Retaining `N-1` (`1.5.1/`) is standard managed-install rollback hygiene and avoids fighting `pi update --all`.

## Risks / Trade-offs

- **2 active Ultra accounts (`0532bad4`, `338764b8`) on Argon/Carbon**: Pruning `62af823b` reduces Ultra capacity from 3 to 2 accounts, which is unavoidable because `62af823b` is banned (`403`/`401`) and currently causes `503` failures (`03:01:09Z` logs) when hit.
- **Codex large-context TPM quota**: Even under `quota-weighted`, running `codex exec` with all MCP servers enabled (~390k tokens) can hit Antigravity per-minute TPM caps; isolated verification probes must use `-c mcp_servers.mcp_router.enabled=false -c features.memories=false -c features.hooks=false` (`~2k–36k` tokens) and clean cooldown state.
- **Concurrent dirty files in `openspec-store`**: `refresh-knowledge-indexes.sh --force` handles GitNexus indexing on dirty repos safely via `--force` without modifying working-tree files; commits in `openspec-store` and `wiki` must remain strictly path-scoped.
