# Design

## Context

See `proposal.md` — Why, and `specs/omniroute-compression-and-routing/spec.md` and `specs/pi-agent-harness-config/spec.md` for normative requirements.

This design builds directly on the established workstation patterns:
- **OmniRoute Startup-Idempotent Runtime Patching (`2026-10-24-align-omniroute-official-runtime-standards`, `2026-10-31-optimize-pi-v1-4-runtime-and-ecosystem-alignment`)**: Runtime fixes for the `omniroute` Docker container (`diegosouzapw/omniroute:latest`) are applied idempotently to compiled Next.js server chunks via untracked `~/Omniroute/scripts/container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`) with fail-closed `requiredMarkers` verification, keeping `git -C ~/Omniroute status --short` clean of tracked modifications.
- **Pi-Native Resource & Provider Resolution (`2026-10-03-pi-config-native-migration-and-skills-placement`, `pi-agent-harness-config`)**: Pi v1.4.0 (`@earendil-works/pi-coding-agent`) natively manages settings (`~/.pi/agent/settings.json`), custom model catalogs (`~/.pi/agent/models.json`), MCP servers (`~/.pi/agent/mcp.json`), and skill filtering (`globalSettings.skills` override patterns in `DefaultPackageManager`).
- **Workspace Skill & GitNexus Group Governance (`agent-skill-distribution`, `refresh-gitnexus-index-groups`, `gitnexus-stable-contract`)**: `/Users/androidteam/Developer/.agents/skills/`, `~/.agents/skills/`, and `/Users/androidteam/Developer/.gitnexus` (which stores `groups/workspace/` and `registry.json`) are governed by workspace-wide contracts and `sync-workspace-agent-skills.py --check`. Pi-specific adjustments must use Pi configuration surfaces rather than deleting shared skill directories or `.gitnexus` group state on disk.

### Transaction & State Boundaries

This change spans three isolated state boundaries with no cross-boundary distributed transaction:
1. **OmniRoute Container Runtime Patch (`~/Omniroute/scripts/container-entrypoint-compat.sh` -> container `omniroute`)**: Atomic update to untracked `container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`), applied in-place via `/app/container-entrypoint-compat.sh --patch-only` followed by container restart and fail-closed `requiredMarkers` + health verification (`docker inspect omniroute`).
2. **Pi User Configuration & Extension State (`~/.pi/agent/`, `~/.pi/`)**: Pre-flight backup to `/tmp/pi-harden-backup/` (`0700`) before atomic writes to `~/.pi/agent/settings.json` (`0600`), `~/.pi/agent/models.json` (`0600`), `~/.pi/agent/web-search.json` (`0600`), `~/.pi/agent/trust.json` (`0644`), `~/.pi/pi-gitnexus.json` (`0600`), and `~/.pi/agent/extensions/agentmemory/index.js`.
3. **Workstation Knowledge & Notion Sync (`~/.hermes/skills/`, `~/Developer/wiki/` -> Notion)**: Updates to `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` and `~/Developer/wiki/entities/pi.md`, followed by idempotent Notion synchronization (`sync-notion-knowledge.sh --section entities` -> page `3efc4b21-deb4-8129-b9c3-d7c22a453212`).

## Goals / Non-Goals

**Goals:**
- Preserve 100% of non-shell tool outputs (`subagent`, `codemode`, `pi-lens`, `gitnexus_*`, `memory_*`, `web_search`, `fetch_content`, `read`, `glob`, `grep`, `write`, `edit`) across OmniRoute's `/v1/responses` `default-caveman` stacked compression pipeline while preserving `bash` command metadata across `adaptBodyForCompression`.
- Activate `pi-web-access` v0.46.0's `searchRouting` (`["exa", "brave", "tavily"]`) and `firecrawl` (`isFirecrawlAvailable() === true`) without blocking top-level searches on the interactive Curator server.
- Prevent `pi-gitnexus` (`0.6.4`) from spawning per-tool `gitnexus augment` subprocesses, appending empty `GitNexus Augment (1.6.12)` banners, or leaving `forceSystemPrompt` set after `before_agent_start`.
- Enable `supportsMidConvoSystemMessages: true` across custom providers in `~/.pi/agent/models.json` (plus `supportsLongCacheRetention: true` on `omniroute-responses`) so mid-session `SystemPromptSections` patches do not rewrite byte 0 of the leading system prompt.
- Exclude the 44 non-symlinked OmniRoute internal CLI skills (`!**/cli-*`, `!**/omni-*`) from Pi's `<available_skills>` prompt section, advertise the 5 core specialist subagents (`scout`, `researcher`, `reviewer`, `oracle`, `worker`), and trust `/Users/androidteam/Omniroute` in `~/.pi/agent/trust.json`.

**Non-Goals:**
- Modifying git-tracked files in `/Users/androidteam/Omniroute`, modifying files inside `~/.pi/agent/npm/node_modules/`, or deleting `/Users/androidteam/Developer/.gitnexus` or skill directories on disk.

## Decisions

### Decision 1: Extract `toolName` and `command` in `markCodexResponseEligibility` Before `delete t.input` and Gate `eligible` / `_rtkSkip` by Shell-Tool Regex

- **Choice**: In `~/Omniroute/scripts/container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`), update the `markCodexResponseEligibility` replacement rule in chunks `14211.js`, `41669.js`, `72459.js`, `88137.js`, and `98542.js` so that during the `for (let a of b)` scan over `inputItems`:
  1. For each `type === "function_call"` item, extract `toolName` (`b`) and parse `arguments.command` / `arguments.cmd` into a `call_id -> command` map (`_cmdMap`).
  2. Test whether `toolName` matches the shell-tool regex `/\b(bash|shell|terminal|run_command|execute_command|exec|command)\b/i`.
  3. On each adapted `function_call_output` message `c`, set `a.eligible = k.length > 0 && g.has(k) && !h.has(k) && _isShell`, `c.tool_call_id = k`, `c._toolCommand = _cmdMap.get(k) || null`, and `c._rtkSkip = !_isShell || !a.eligible`.
  4. In `applyRtkCompression` (`53846.js` and `72459.js`), update the `role === "tool"` branch to `({command:b,skipFilters:c}=z(d,m)),a._toolCommand&&!b&&(b=a._toolCommand),a._rtkSkip&&(c=!0)`.
- **Rationale**: In `strategySelector.ts`, `adaptBodyForCompression(body)` runs once before `applyStackedCompression` and deletes `body.input` (`delete t.input`). Consequently, `applyRtkCompression` never sees `a.input` in stacked mode, leaving its internal `toolCallLookup` (`m`) empty. Furthermore, `DEFAULT_CODEX_PROTECTED_TOOL_NAMES` only lists 9 basic file/web tools (`read`, `glob`, `grep`, `write`, `edit`, `websearch`, `webfetch`, `web_search`, `web_fetch`), so every other non-shell tool in Pi (`subagent`, `codemode`, `pi-lens`, `gitnexus_*`, `memory_*`, `intercom`) previously received `a.eligible = true` and `c._rtkSkip = false`, causing `rtk`'s `npm-audit` filter and `codex-responses`'s `collapseLines` to strip up to 93% of lines from `subagent({ action: "list" | "models" | "doctor" })`. Computing `_isShell` and `_toolCommand` inside `markCodexResponseEligibility` (while `inputItems` is still present) protects every non-shell tool across both `codex-responses` and `rtk` and preserves `bash` command metadata into `applyRtkCompression`.
- **Alternatives Considered**:
  - *Add `"subagent"`, `"codemode"`, etc. one-by-one to `DEFAULT_CODEX_PROTECTED_TOOL_NAMES`*: Rejected — brittle allowlist that misses new extension tools and still loses `bash` `command` metadata because `body.input` is deleted before `applyRtkCompression` runs.

### Decision 2: Omit `"provider"` and Configure `firecrawlBaseUrl` and `workflow: "none"` in `~/.pi/agent/web-search.json`

- **Choice**: Update `~/.pi/agent/web-search.json` (`0600`) to remove `"provider": "exa"`, add `"firecrawlBaseUrl": "https://api.firecrawl.dev"`, change `"workflow": "summary-review"` to `"workflow": "none"`, and update `"searchModel"` from `"gemini-2.5-flash"` to `"gemini-3.6-flash"`.
- **Rationale**: In `pi-web-access` v0.46.0 (`gemini-search.ts:169, 234–237, 810–821`), `config.searchProviderConfigured` is `Object.hasOwn(raw, "searchProvider") || Object.hasOwn(raw, "provider")`, and `getConfiguredSearchRouting()` returns `undefined` whenever `searchProviderConfigured` is `true`. Removing `"provider": "exa"` leaves `searchProvider` at `"auto"` and activates `searchWithConfiguredRouting()` with `searchRouting.providers: ["exa", "brave", "tavily"]`—keeping Exa as the primary provider while enabling automatic fallback to Brave and Tavily on `transient`, `quota`, `network`, or `invalid-response` errors. Adding `"firecrawlBaseUrl": "https://api.firecrawl.dev"` satisfies `firecrawl.ts:isFirecrawlAvailable()` (`getBaseUrl() !== null`). Setting `"workflow": "none"` prevents top-level `web_search` calls from blocking for 20s on the interactive Curator browser server.
- **Alternatives Considered**:
  - *Keep `"provider": "exa"`*: Rejected — completely disables `searchRouting` fallback in `pi-web-access` v0.46.0.

### Decision 3: Disable `pi-gitnexus` `autoAugment` via `~/.pi/pi-gitnexus.json` and Intercept Static `forceSystemPrompt` Suffixes in `agentmemory/index.js`

- **Choice**:
  1. Create `~/.pi/pi-gitnexus.json` (`0600`) with `{"autoAugment": false}`.
  2. In `~/.pi/agent/extensions/agentmemory/index.js` (`before_agent_start`, which runs at user extension precedence rank `3` before package extensions at rank `4`), install an idempotent property descriptor on `event.systemPromptOptions.forceSystemPrompt` that intercepts any string assignment `val` starting with the rendered base system prompt (`buildSystemPrompt`) followed by a static suffix (such as `pi-gitnexus`'s `\n\n[GitNexus active] ...`), appends the trimmed suffix to `event.systemPromptOptions.promptGuidelines` (if not already present), and keeps `forceSystemPrompt` as `undefined`.
- **Rationale**: `pi-gitnexus` (`0.6.4`) reads `~/.pi/pi-gitnexus.json` on `session_start` (`augmentEnabled = cfg.autoAugment !== false`); setting `"autoAugment": false` cleanly disables the `tool_result` hook that spawns `gitnexus augment` on every `read`/`grep`/`find`/`bash` call and appends empty `GitNexus Augment (1.6.12)` banners, while keeping all 7 explicit `gitnexus_*` tools active. Meanwhile, because `pi-gitnexus`'s `before_agent_start` handler unconditionally returns `{ systemPrompt: event.systemPrompt + "\n\n[GitNexus active] ..." }`, intercepting `currentOptions.forceSystemPrompt` on `event.systemPromptOptions` converts that static suffix into a structured `promptGuidelines` rule without modifying files inside `~/.pi/agent/npm/node_modules/pi-gitnexus/`.
- **Alternatives Considered**:
  - *Edit `~/.pi/agent/npm/node_modules/pi-gitnexus/src/index.ts` directly*: Rejected — `pi update --all` overwrites `node_modules`.
  - *Delete `/Users/androidteam/Developer/.gitnexus`*: Rejected — `/Users/androidteam/Developer/.gitnexus` stores `groups/workspace/bridge.lbug` and `registry.json` governed by `refresh-gitnexus-index-groups`.

### Decision 4: Enable `supportsMidConvoSystemMessages: true` in `~/.pi/agent/models.json` and Configure `skills` Exclusions + Subagent `advertise: true` in `~/.pi/agent/settings.json`

- **Choice**:
  1. In `~/.pi/agent/models.json`, add `"compat": { "supportsLongCacheRetention": true, "supportsMidConvoSystemMessages": true }` to `omniroute-responses`, and add `"supportsMidConvoSystemMessages": true` to the `compat` blocks of `cockpit`, `omniroute`, `phanmemvip`, `shopapikey`, and `omniroute-anthropic`.
  2. In `~/.pi/agent/settings.json`, add `"skills": ["!**/cli-*", "!**/omni-*"]` and update `subagents.agentOverrides` to include `"advertise": true` on `scout`, `researcher`, `reviewer`, `oracle`, and `worker` (adding `worker: { "model": "omniroute-responses/gemini-3.8-flash-high", "thinking": "high", "advertise": true }`).
  3. In `~/.pi/agent/trust.json`, add `"/Users/androidteam/Omniroute": true`.
- **Rationale**: In `@earendil-works/pi-ai`, custom models default to `supportsMidConvoSystemMessages: false`, which forces `collapseSystemMessages(transcript)` to fold mid-conversation section updates into byte 0 of the leading system prompt. Enabling `supportsMidConvoSystemMessages: true` keeps mid-session section updates (`active_subagents`, `advertised_subagents`, `selectedTools`) as incremental messages that preserve the cached prefix. Adding `"skills": ["!**/cli-*", "!**/omni-*"]` uses `DefaultPackageManager`'s `userOverrides.skills` pattern matcher to disable the 44 non-symlinked OmniRoute CLI skills in `~/.agents/skills/` (reducing Pi's skill count from 196 to 152) without touching `~/.agents/skills/` on disk or affecting `sync-workspace-agent-skills.py --check`.

## Risks / Trade-offs

- **[Risk] Intercepting `forceSystemPrompt` on `event.systemPromptOptions` could affect an extension that intentionally replaces the entire system prompt** → **Mitigation**: Only convert `forceSystemPrompt` into `promptGuidelines` when the assigned string strictly starts with the current rendered system prompt (or contains `[GitNexus active]`); if an extension assigns a genuinely different replacement prompt, preserve `forceSystemPrompt` as-is.
- **[Risk] Restricting `a.eligible` in `markCodexResponseEligibility` to shell tools changes `codex-responses` eligibility for custom non-shell tools** → **Mitigation**: Both `rtk` (`SHELL_TOOL_NAME_RE`) and `codex-responses` are designed for shell/build/test outputs; non-shell tools in Pi return structured code, outlines, or agent reports that must not have lines dropped by log/audit filters.

## Migration Plan

1. **Pre-Flight Backup**: Create `/tmp/pi-harden-backup/` (`0700`) and copy `~/Omniroute/scripts/container-entrypoint-compat.sh`, `~/.pi/agent/{settings,models,web-search,trust}.json`, and `~/.pi/agent/extensions/agentmemory/index.js`.
2. **OmniRoute `/v1/responses` Patch**: Update `~/Omniroute/scripts/container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`), apply to container `omniroute`, restart `omniroute`, and verify `docker inspect omniroute` (`healthy`) plus an in-container stacked compression check on `subagent` (`list`, `models`, `doctor`) and `bash` payloads.
3. **Pi Configuration & Extension Updates**: Write `~/.pi/pi-gitnexus.json` (`0600`), `~/.pi/agent/web-search.json` (`0600`), `~/.pi/agent/models.json` (`0600`), `~/.pi/agent/settings.json` (`0600`), `~/.pi/agent/trust.json` (`0644`), and `~/.pi/agent/extensions/agentmemory/index.js`.
4. **Documentation & Notion Sync**: Update `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` and `~/Developer/wiki/entities/pi.md`, then run `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh --section entities`.
5. **Rollback**: Restore files from `/tmp/pi-harden-backup/` and re-run `ensure-muse-wire-compat.sh` + restart `omniroute` if any verification gate fails.
