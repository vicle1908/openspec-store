# Design

## Context

See `proposal.md` — Why, and `specs/omniroute-compression-and-routing/spec.md` and `specs/pi-agent-harness-config/spec.md` for normative requirements.

This design builds directly on the established workstation patterns:
- **OmniRoute Startup-Idempotent Runtime Patching (`2026-10-24-align-omniroute-official-runtime-standards`, `2026-10-31-optimize-pi-v1-4-runtime-and-ecosystem-alignment`)**: Runtime fixes for the `omniroute` Docker container (`diegosouzapw/omniroute:latest`) are applied idempotently to compiled Next.js server chunks via untracked `~/Omniroute/scripts/container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`) with fail-closed `requiredMarkers` verification, keeping `git -C ~/Omniroute status --short` clean of tracked modifications.
- **Pi-Native Resource & Provider Resolution (`2026-10-03-pi-config-native-migration-and-skills-placement`, `pi-agent-harness-config`)**: Pi v1.4.0 (`@earendil-works/pi-coding-agent`) natively manages settings (`~/.pi/agent/settings.json`), custom model catalogs (`~/.pi/agent/models.json`), MCP servers (`~/.pi/agent/mcp.json`), and skill filtering (`globalSettings.skills` override patterns in `DefaultPackageManager`).
- **Workspace Skill & GitNexus Group Governance (`agent-skill-distribution`, `refresh-gitnexus-index-groups`, `gitnexus-stable-contract`)**: `/Users/androidteam/Developer/.agents/skills/`, `~/.agents/skills/`, and `/Users/androidteam/Developer/.gitnexus` (which stores `groups/workspace/` and `registry.json`) are governed by workspace-wide contracts and `sync-workspace-agent-skills.py --check`. Pi-specific adjustments must use Pi configuration surfaces rather than deleting shared skill directories or `.gitnexus` group state on disk.

### Transaction & State Boundaries

This change spans three isolated state boundaries with no cross-boundary distributed transaction:
1. **OmniRoute Container Runtime Patch (`~/Omniroute/scripts/container-entrypoint-compat.sh` -> container `omniroute`)**: Atomic update to untracked `container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`) including synchronized `requiredMarkers`, applied in-place via `/app/container-entrypoint-compat.sh --patch-only` followed by container restart and fail-closed `requiredMarkers` + health verification (`docker inspect omniroute`).
2. **Pi User Configuration & Extension State (`~/.pi/agent/`, `~/.pi/`, `~/.pi-lens/`)**: Pre-flight backup to `/tmp/pi-harden-backup/` (`0700`) before atomic writes to `~/.pi/agent/settings.json` (`0600`), `~/.pi/agent/models.json` (`0600`), `~/.pi/agent/web-search.json` (`0600`), `~/.pi/agent/trust.json` (`0644`), `~/.pi/pi-gitnexus.json` (`0600`), and `~/.pi/agent/extensions/agentmemory/index.js`.
3. **Workstation Automation & Knowledge (`~/Developer/scripts/`, `~/.hermes/skills/`, `~/Developer/wiki/` -> Notion)**: Byte-identical updates to `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh`, updates to `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` and `~/Developer/wiki/entities/pi.md`, and idempotent Notion synchronization (`sync-notion-knowledge.sh --section entities` -> page `3efc4b21-deb4-8129-b9c3-d7c22a453212`).

## Goals / Non-Goals

**Goals:**
- Preserve 100% of non-shell and custom/patch tool outputs (`subagent`, `codemode`, `pi-lens`, `gitnexus_*`, `memory_*`, `web_search`, `fetch_content`, `read`, `glob`, `grep`, `write`, `edit`, `custom_tool_call_output`, `apply_patch_call_output`) across OmniRoute's `/v1/responses` `default-caveman` stacked compression pipeline while preserving `bash` command metadata across `adaptBodyForCompression`.
- Activate `pi-web-access` v0.46.0's `searchRouting` (`["exa", "brave", "tavily"]`) and `firecrawl` (`isFirecrawlAvailable() === true`) without blocking top-level searches on the interactive Curator server.
- Prevent `pi-gitnexus` (`0.6.4`) from spawning per-tool `gitnexus augment` subprocesses, appending empty `GitNexus Augment (1.6.12)` banners, or leaving `forceSystemPrompt` set after `before_agent_start`, while preserving child subagent `<active_agent>` boundary prompts and skipping `agentmemory` network calls inside child subagents.
- Enable `supportsMidConvoSystemMessages: true` across custom providers in `~/.pi/agent/models.json` (plus `supportsLongCacheRetention: true` on `omniroute-responses`) so mid-session `SystemPromptSections` patches do not rewrite byte 0 of the leading system prompt.
- Exclude the 44 non-symlinked OmniRoute internal CLI skills (`!**/cli-*`, `!**/omni-*`) from Pi's `<available_skills>` prompt section, advertise the 5 core specialist subagents (`scout`, `researcher`, `reviewer`, `oracle`, `worker`), trust `/Users/androidteam/Omniroute` in `~/.pi/agent/trust.json`, and cap `~/.pi-lens/*.log` files at 5 MB in `workstation-daily-update.sh`.

**Non-Goals:**
- Modifying git-tracked files in `/Users/androidteam/Omniroute`, modifying files inside `~/.pi/agent/npm/node_modules/`, or deleting `/Users/androidteam/Developer/.gitnexus` or skill directories on disk.

## Decisions

### Decision 1: Extract `toolName` and `command` in `markCodexResponseEligibility` Before `delete t.input`, Protect `custom_tool_call_output`/`apply_patch_call_output`, and Synchronize `requiredMarkers`

- **Choice**: In `~/Omniroute/scripts/container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`), update the `markCodexResponseEligibility` replacement rule in chunks `14211.js`, `41669.js`, `72459.js`, `88137.js`, and `98542.js` so that:
  1. During the `for (let a of b)` scan over `inputItems`, for each `type === "function_call"` item, extract `toolName` (`b`) into `g` and parse `arguments.command` / `arguments.cmd` into a `call_id -> command` map (`_cmdMap`).
  2. In the `for (let c of a)` loop over adapted messages:
     - For `apply_patch_call_output` and `custom_tool_call_output`, set `c._rtkSkip = true` before the `if ("function_call_output" !== a.type) continue` guard so RTK never runs shell filters on patch or grammar-constrained custom tool outputs.
     - For `function_call_output`, test whether `g.get(k)` matches `/\b(bash|shell|terminal|run_command|execute_command|exec|command)\b/i` (`_sh`). Set `a.eligible = k.length > 0 && g.has(k) && !h.has(k) && _sh`, `c.tool_call_id = k`, `c._toolCommand = _cmdMap.get(k) || null`, and `c._rtkSkip = !_sh || !a.eligible`.
  3. In `applyRtkCompression` (`53846.js` and `72459.js`), update the `role === "tool"` branch to `({command:b,skipFilters:c}=z(d,m)),a._toolCommand&&!b&&(b=a._toolCommand),a._rtkSkip&&(c=!0)`.
  4. Update the five `responses_tool_call_id_{14211,41669,72459,88137,98542}` and two `rtk_stacked_meta_skip_{53846,72459}` entries in `requiredMarkers` inside `container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`) to match the new replacement patterns.
- **Rationale**: In `strategySelector.ts`, `adaptBodyForCompression(body)` runs once before `applyStackedCompression` and deletes `body.input` (`delete t.input`). Computing `_sh` and `_toolCommand` inside `markCodexResponseEligibility` (while `inputItems` is still present) protects every non-shell and custom tool across both `codex-responses` and `rtk`, preserves `bash` command metadata into `applyRtkCompression`, and keeps fail-closed startup marker verification green.
- **Alternatives Considered**:
  - *Add `"subagent"`, `"codemode"`, etc. one-by-one to `DEFAULT_CODEX_PROTECTED_TOOL_NAMES`*: Rejected — brittle allowlist that misses new extension tools, leaves `custom_tool_call_output` unprotected, and still loses `bash` `command` metadata because `body.input` is deleted before `applyRtkCompression` runs.

### Decision 2: Omit `"provider"` and Configure `firecrawlBaseUrl` and `workflow: "none"` in `~/.pi/agent/web-search.json`

- **Choice**: Update `~/.pi/agent/web-search.json` (`0600`) to remove `"provider": "exa"`, add `"firecrawlBaseUrl": "https://api.firecrawl.dev"`, change `"workflow": "summary-review"` to `"workflow": "none"`, and update `"searchModel"` from `"gemini-2.5-flash"` to `"gemini-3.6-flash"`.
- **Rationale**: In `pi-web-access` v0.46.0 (`gemini-search.ts:169, 234–237, 810–821`), `config.searchProviderConfigured` is `Object.hasOwn(raw, "searchProvider") || Object.hasOwn(raw, "provider")`, and `getConfiguredSearchRouting()` returns `undefined` whenever `searchProviderConfigured` is `true`. Removing `"provider": "exa"` leaves `searchProvider` at `"auto"` and activates `searchWithConfiguredRouting()` with `searchRouting.providers: ["exa", "brave", "tavily"]`—keeping Exa as the primary provider while enabling automatic fallback to Brave and Tavily on `transient`, `quota`, `network`, or `invalid-response` errors. Adding `"firecrawlBaseUrl": "https://api.firecrawl.dev"` satisfies `firecrawl.ts:isFirecrawlAvailable()` (`getBaseUrl() !== null`). Setting `"workflow": "none"` prevents top-level `web_search` calls from blocking for 20s on the interactive Curator browser server.
- **Alternatives Considered**:
  - *Keep `"provider": "exa"`*: Rejected — completely disables `searchRouting` fallback in `pi-web-access` v0.46.0.

### Decision 3: Disable `pi-gitnexus` `autoAugment` via `~/.pi/pi-gitnexus.json`, Intercept Only the Exact `[GitNexus active]` Suffix on `forceSystemPrompt`, and Skip `agentmemory` Network Calls in Child Subagents

- **Choice**:
  1. Create `~/.pi/pi-gitnexus.json` (`0600`) with `{"autoAugment": false}`.
  2. In `~/.pi/agent/extensions/agentmemory/index.js` (`before_agent_start`, which runs at user extension precedence rank `3` before package extensions at rank `4`), install an idempotent property descriptor on `event.systemPromptOptions.forceSystemPrompt` that checks whether the assigned string ends with `pi-gitnexus`'s exact `\n\n[GitNexus active] ...` notice. When matched, strip that suffix, push `[GitNexus active] ...` into `event.systemPromptOptions.promptGuidelines` (if not already present), and keep `forceSystemPrompt` `undefined` (or set to the stripped string only if a prior handler had already set a non-empty `forceSystemPrompt`). Any other `forceSystemPrompt` value—such as `pi-subagents` child boundary prompts containing `<active_agent` (`herdr-pi-bridge.js:164`) or `Subagent Execution Boundary` (`subagent-prompt-runtime.js:242`)—is stored in `forceSystemPrompt` unchanged.
  3. Add a `isChildSubagent(ctx)` helper in `agentmemory/index.js` checking `Boolean(process.env.PI_SUBAGENT_CHILD) || Boolean(ctx?.sessionManager?.getHeader?.()?.parentSession)` so `before_agent_start` and `agent_end` skip `smart-search` and `observe` network calls inside child subagents while still pushing `TOOL_GUIDANCE` into `promptGuidelines`.
- **Rationale**: Matching only the exact `[GitNexus active]` suffix prevents `pi-subagents` child boundary prompts (`<active_agent .../>`) from being misclassified and turned into a bullet inside `<rules>`. Skipping `smart-search` and `observe` in child subagents matches the child-session guards in `orca-agent-status.ts` and `herdr-agent-state.ts`, eliminating 8x fan-out load on `localhost:3111` during parallel subagent runs and preventing child scratch work from polluting long-term memory.
- **Alternatives Considered**:
  - *Wildcard suffix matching on `forceSystemPrompt`*: Rejected — `pi-subagents` also appends `<active_agent>` and boundary blocks to `event.systemPrompt` in child sessions; wildcard suffix matching would corrupt child subagent instructions.
  - *Edit `~/.pi/agent/npm/node_modules/pi-gitnexus/src/index.ts` directly*: Rejected — `pi update --all` overwrites `node_modules`.

### Decision 4: Enable `supportsMidConvoSystemMessages: true` in `~/.pi/agent/models.json`, Configure `skills` Exclusions + Subagent `advertise: true` in `settings.json`, and Bound `~/.pi-lens/*.log` in `workstation-daily-update.sh`

- **Choice**:
  1. In `~/.pi/agent/models.json`, add `"compat": { "supportsLongCacheRetention": true, "supportsMidConvoSystemMessages": true }` to `omniroute-responses`, and add `"supportsMidConvoSystemMessages": true` to the `compat` blocks of `cockpit`, `omniroute`, `phanmemvip`, `shopapikey`, and `omniroute-anthropic`.
  2. In `~/.pi/agent/settings.json`, add `"skills": ["!**/cli-*", "!**/omni-*"]` and update `subagents.agentOverrides` to include `"advertise": true` on `scout`, `researcher`, `reviewer`, `oracle`, and `worker` (adding `worker: { "model": "omniroute-responses/gemini-3.8-flash-high", "thinking": "high", "advertise": true }`).
  3. In `~/.pi/agent/trust.json`, add `"/Users/androidteam/Omniroute": true`.
  4. In `~/Developer/scripts/workstation-daily-update.sh` (and `platform/openspec-store/scripts/workstation-daily-update.sh`), add a maintenance check that truncates any `~/.pi-lens/*.log` file larger than 5 MB (`5242880` bytes).
- **Rationale**: Enabling `supportsMidConvoSystemMessages: true` keeps mid-session section updates (`active_subagents`, `advertised_subagents`, `selectedTools`) as incremental messages that preserve the cached prefix. Adding `"skills": ["!**/cli-*", "!**/omni-*"]` disables the 44 non-symlinked OmniRoute CLI skills in `~/.agents/skills/` (reducing Pi's skill count from 196 to 152) without touching `~/.agents/skills/` on disk. Truncating `~/.pi-lens/*.log` files >5 MB in `workstation-daily-update.sh` prevents unbounded log growth across daily multi-agent runs.

## Risks / Trade-offs

- **[Risk] A future `pi-gitnexus` version could change the wording of its `[GitNexus active]` suffix** → **Mitigation**: Match the `\n\n[GitNexus active]` prefix at the tail of the assigned `forceSystemPrompt` string so minor trailing wording updates still convert cleanly while `<active_agent` child boundary prompts are never matched.
- **[Risk] Restricting `a.eligible` in `markCodexResponseEligibility` to shell tools changes `codex-responses` eligibility for custom non-shell tools** → **Mitigation**: Both `rtk` (`SHELL_TOOL_NAME_RE`) and `codex-responses` are designed for shell/build/test outputs; non-shell tools in Pi return structured code, outlines, or agent reports that must not have lines dropped by log/audit filters.

## Migration Plan

1. **Pre-Flight Backup**: Create `/tmp/pi-harden-backup/` (`0700`) and copy `~/Omniroute/scripts/container-entrypoint-compat.sh`, `~/Omniroute/scripts/ensure-muse-wire-compat.sh`, `~/.pi/agent/{settings,models,web-search,trust}.json`, and `~/.pi/agent/extensions/agentmemory/index.js`.
2. **OmniRoute `/v1/responses` Patch**: Update `~/Omniroute/scripts/container-entrypoint-compat.sh` and `~/Omniroute/scripts/ensure-muse-wire-compat.sh` (including `requiredMarkers`), apply to container `omniroute`, restart `omniroute`, and verify `docker inspect omniroute` (`healthy`) plus an in-container stacked compression check on `subagent` (`list`, `models`, `doctor`), `custom_tool_call_output`, and `bash` payloads.
3. **Pi Configuration & Extension Updates**: Write `~/.pi/pi-gitnexus.json` (`0600`), `~/.pi/agent/web-search.json` (`0600`), `~/.pi/agent/models.json` (`0600`), `~/.pi/agent/settings.json` (`0600`), `~/.pi/agent/trust.json` (`0644`), and `~/.pi/agent/extensions/agentmemory/index.js`.
4. **Daily Updater, Documentation & Notion Sync**: Update `~/Developer/scripts/workstation-daily-update.sh` and its mirror in `platform/openspec-store/scripts/workstation-daily-update.sh`, update `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` and `~/Developer/wiki/entities/pi.md`, and run `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh --section entities`.
5. **Rollback**: Restore files from `/tmp/pi-harden-backup/` and re-run `ensure-muse-wire-compat.sh` + restart `omniroute` if any verification gate fails.
