# Proposal

## Why

OmniRoute (`v3.8.52`) currently leaves key resilience, routing, and compression features either dormant or partially misconfigured: `strategy: "auto"` combos set only `resetAwareQuotaCacheTtlMs` while `resolveAutoResetWindowConfig` (`quotaScoring.ts:95-119`) actually reads `resetWindowQuotaCacheTtlMs`, several combos (`gemini-4-argon`, `muse-spark-1.3`, `claude-opus-5.5`, `phanmemvip`) flatten nested `combo-ref` targets, include an unentitled account (`62af823b`) in `gemini-4-argon`, or route 50% of turns to inactive connections, `thinkingBudget.mode` is set to `"adaptive"` instead of the officially recommended `"passthrough"` for coding CLIs (`THINKING_BUDGET.md`), the secondary API bridge (`API_PORT=20129`) binds to container-internal `127.0.0.1` instead of `0.0.0.0` (`API_HOST=0.0.0.0`), high-value resilience feature flags remain default-off, and installed `omni-*`/`cli-*` skills carry outdated v3.8.52 payload examples while `sync-workspace-agent-skills.py --check` fails on `surface_violations=data/skills`. Aligning the live OmniRoute configuration, OpenSpec artifacts, and agent skills with official v3.8.52 documentation and route schemas eliminates quota-polling stalls, pin-escape warnings, port-20129 connection drops, and skill drift.

## What Changes

- **Dual Quota-Cache Key & Two-Ultra-Account Alignment on Auto Combos**:
  - Set both `resetAwareQuotaCacheTtlMs: 300000` / `resetAwareQuotaCacheMaxStaleMs: 3600000` AND `resetWindowQuotaCacheTtlMs: 300000` / `resetWindowQuotaCacheMaxStaleMs: 3600000` across all `agy`-backed combos (`gemini-3.8-flash-high`, `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, `claude-opus-5.5`, `muse-spark-1.3`) while preserving existing `config` fields (`sqliteComboRepository.ts` shallow-merge invariant).
  - Reconcile `gemini-4-argon` (`f1cefc64-7662-4f0a-9234-84f70603cbe4`), `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` to `strategy: "auto"`, `context_cache_protection: false`, and strictly the **two** canonical Google AI `Ultra` `agy` CLI connections (`338764b8-1cd7-4946-b789-ee5dad4c5073` / `vinhghtk1908@gmail.com` and `0532bad4-2486-4286-8f06-510e9c678620` / `vinhvumobile@gmail.com`) per `omniroute-agent-cli-routing/spec.md:637-648`.
- **Combo Strategy, Nested Execution, Container Bridge Port & Connection Hygiene**:
  - Set `muse-spark-1.3` (`453c5dd3-f7f4-4c44-bd4b-6c3c1d0f4e5b`) to `strategy: "priority"`, `context_cache_protection: false`, and `config.nestedComboMode: "execute"` so its primary `combo-ref: gemini-3.8-flash-high` step runs its encapsulated 16-factor `auto` strategy before falling back to `agy/gemini-3.8-flash-medium`.
  - Set `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) to `strategy: "auto"`, `context_cache_protection: false`, and `config.nestedComboMode: "flatten"` across all 8 active `agy/claude-opus-5-5-high` accounts + `combo-ref: gemini-3.8-flash-high` so 16-factor `auto` scoring (`tierPriority: Ultra=1.0, Pro=0.67`) and `applySessionStickiness` load-balance and pin across all 8 Opus accounts while keeping Flash in the fallback tail.
  - Prune the dead disabled-provider step (`openai-compatible-responses-4b50733f-f160-4f63-bf71-088b0bd469ab/gpt-5.6-sol`) from `phanmemvip` (`ad4dace4-9072-42a8-8503-e6188e325890`) and set `isActive: false` on the expired `codex` connection (`0ee99889-6643-4fe8-a68a-6c4350de961f`) via `PATCH /api/providers/{id}` (while intentionally preserving `muse-code` `51795cf9-4c03-4c22-af9d-9ce4de975dc1` active for `/v1/muse-code/models` catalog discovery).
  - Add `API_HOST=0.0.0.0` to `~/Omniroute/docker-compose.override.yml` so `apiBridgeServer.ts` listens on container `0.0.0.0:20129` (mapped exclusively to host `127.0.0.1:20129:20129`), allowing host port `20129` (`cockpit` launcher and API bridge) to serve requests alongside port `20128`.
- **RTK Tool-Result Compression, Adaptive Context Budget & Delegated Context Editing**:
  - Enable RTK in `minimal` intensity for tool results only (`enabled: true`, `preserveSystemPrompt: true`, `engines.rtk: {enabled: true, level: "minimal"}`, `rtkConfig: {enabled: true, intensity: "minimal", applyToToolResults: true, applyToCodeBlocks: false, applyToAssistantMessages: false, maxLinesPerResult: 120, maxCharsPerResult: 12000, deduplicateThreshold: 3, preserveDocstrings: true}`), configure `contextBudget: {mode: "replace-autotrigger", policy: "reserve-output", outputReserve: 4096, safetyMargin: 1024, pct: 0.85, absoluteBudget: 0}` so requests exceeding 85% of model context window automatically escalate along the compression ladder (while headerless normal-size requests run lossless `SAFE_DEFAULT_PIPELINE`: `session-dedup` + `lite` unless `x-omniroute-compression: allow-lossy` or `engine:rtk` is sent), and enable `contextEditing: {enabled: true}` (`clear_tool_uses_20250919`) for long Claude tool loops.
- **Thinking Budget, Cache, Database Backup & Feature Flag Hardening**:
  - Switch `thinkingBudget.mode` to `"passthrough"` per `docs/guides/THINKING_BUDGET.md` so coding CLIs (Codex, Claude Code, OMP) retain full reasoning control and `reasoning.summary` streams.
  - Point `semanticCacheEmbeddingProvider` / `semanticCacheEmbeddingModel` from unconnected `"lemonade"` to active 1024-dim `voyage-ai` (`voyage-code-3`) via `PUT /api/settings/cache-config`.
  - Enable daily SQLite auto-backups (`backup.autoBackupEnabled: true`, `autoBackupFrequency: "daily"`, `keepLastNBackups: 5`) via `PATCH /api/settings/database`.
  - Enable 5 recommended v3.8.52 resilience feature flags via individual `PUT /api/settings/feature-flags` calls (`{"key": "<FLAG>", "value": "true"}`): `CREDENTIAL_GATE_AUTH_DIAGNOSES_ONLY`, `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED`, `COMBO_EMPTY_POOL_NO_ELIGIBLE_TARGETS_ENABLED`, `STREAM_LATE_OUTPUT_PROBE_ENABLED`, and `RETRY_AFTER_PROVENANCE_ENABLED`.
- **OmniRoute Skills & Workspace Surface Enhancement**:
  - Enhance user-scope `~/.agents/skills/` (`omni-compression`, `omni-context-rtk`, `omni-combos-routing`, `omni-settings`, `omni-resilience`, `omni-auth`, `omni-inference`, `omni-providers`, `cli-health`, `cli-keys`, `cli-routing`) within `<!-- skill:custom-start -->` / `<!-- skill:custom-end -->` markers ($\le 500$ lines per file) while keeping `/Users/androidteam/Omniroute` git-clean.
  - Update `docs/omniroute-agent-skills.md` and `wiki/entities/omniroute.md` (`23 omni-*` REST skills, `55` RTK filters) and unlink the 13 AstrBot-triggered symlinks in `~/Developer/data/skills` so `sync-workspace-agent-skills.py --check` exits `0`.

## Capabilities

### New Capabilities
- `omniroute-compression-and-routing`: Governs prompt compression pipeline activation (RTK tool filters, `lossyRequestPolicy`, `contextBudget` adaptive escalation, delegated `contextEditing`), combo routing resilience (dual quota-cache keys, `nestedComboMode`, connection stickiness), container bridge port `20129` (`API_HOST=0.0.0.0`), thinking-budget passthrough, and resilience feature flags.

### Modified Capabilities
- `omniroute-agent-cli-routing`: Extends combo routing requirements with connection-level stickiness (`context_cache_protection: false`), encapsulated `nestedComboMode: "execute"` on `muse-spark-1.3`, 16-factor `auto` scoring on `claude-opus-5.5`, and container bridge `API_HOST=0.0.0.0` reachability on host loopback port `20129`.
- `omniroute-agent-skills`: Extends OmniRoute skill catalog and workspace surface requirements to cover 23 `omni-*` REST skills, 55 RTK filters, `<!-- skill:custom-start -->` preservation under the 500-line cap, and `data/skills` symlink hygiene.

## Non-Goals

- Replacing or migrating the underlying Docker named volume storage (`omniroute-data`).
- Running `PRAGMA wal_checkpoint(TRUNCATE)` against a live running OmniRoute server (which risks `SIGBUS` per `#13973`).
- Modifying tracked files inside `/Users/androidteam/Omniroute`.

## Ownership Boundaries

- **Affected System**: OmniRoute AI gateway runtime (`http://127.0.0.1:20128` and `20129`, untracked `~/Omniroute/docker-compose.override.yml`), user-level skills (`~/.agents/skills/`), and workspace docs/skills surface (`~/Developer/docs/`, `~/Developer/wiki/`, `~/Developer/data/skills`).
- **Owner**: AI Platform Engineering / Workstation tooling.
- **Client Consumers**: Claude Code, Codex CLI, OMP (Oh My Pi), Goose CLI, Grok Build, Muse Code.

## Impact

- **Performance**: Activates true 5-minute stale-while-revalidate quota caching on `strategy: "auto"` combos via `resetWindowQuotaCacheTtlMs`; enables lossless `SAFE_DEFAULT_PIPELINE` by default plus automatic RTK/ladder escalation when context exceeds 85% or when `x-omniroute-compression: allow-lossy` / `engine:rtk` is sent.
- **Reliability**: Restores host loopback port `20129` reachability (`API_HOST=0.0.0.0` in container), eliminates 50% dead-target routing on `phanmemvip`, load-balances all 8 Opus accounts on `claude-opus-5.5` with `auto` scoring + session stickiness, prevents account pile-up via `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED`, and preserves reasoning streams via `thinkingBudget.mode: "passthrough"`.
- **Breaking Changes**: None.
