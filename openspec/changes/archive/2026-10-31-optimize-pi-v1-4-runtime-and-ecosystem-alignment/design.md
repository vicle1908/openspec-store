# Design

## Context

See `proposal.md` — Why.

The workstation already establishes several governing patterns that this design extends rather than replaces:
- **Pi-Native Resource & Provider Resolution (`2026-10-03-pi-config-native-migration-and-skills-placement`)**: Pi v1.4.0 (`@earendil-works/pi-coding-agent`) natively manages providers (`~/.pi/agent/models.json`), MCP servers (`~/.pi/agent/mcp.json` via `dist/extensions/mcp/index.js`), and skills (`~/.agents/skills/`).
- **Shared Credential Indirection (`2026-08-28-standardize-zshenv-shared-secrets`, `coding-agent-credential-loading`)**: Active shared-tier credentials are exported in `~/.zshenv` (`0600`) and referenced via `$ENV_VAR` / `${ENV_VAR}` indirection rather than stored as inline literals in agent configuration files.
- **On-Demand Ultra Argon Routing & Provider Preservation (`2026-10-20-register-gemini-4-argon-across-coding-agents`, `coding-cli-provider-registry`)**: `omniroute-responses` serves as Pi's primary Responses provider (`defaultModel: "gemini-3.8-flash-high"`), with `gemini-4-argon*` registered for high-reasoning specialist turns and all existing provider blocks (`cockpit`, `omniroute`, `shopapikey`, `phanmemvip`, `omniroute-anthropic`, `omniroute-responses`) preserved.
- **OmniRoute Startup-Idempotent Runtime Patching (`2026-10-24-align-omniroute-official-runtime-standards`)**: Runtime fixes in `~/Omniroute` are applied idempotently to compiled Next.js server chunks inside the running `omniroute` Docker container via untracked `~/Omniroute/scripts/container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`), keeping `git status` on tracked files in `~/Omniroute` clean so `check-upstream.sh` and `update.sh` never fail on a dirty working tree.

### Transaction & State Boundaries

This change spans four isolated filesystem/state boundaries with no shared distributed transaction:
1. **Shared Shell Environment (`~/.zshenv`, mode `0600`)**: Atomic file write with pre-change backup in `/tmp/pi-optimize-backup/`.
2. **Pi User Configuration & Extension State (`~/.pi/agent/`, `~/.pi-lens/`)**: Atomic per-file JSON/JS writes (`0600` on config files) backed up to `/tmp/pi-optimize-backup/` before mutation; stale directory pruning (`releases/1.3.0`, `.bak*`, orphaned `pi-hermes-memory` dirs) is performed only after backups and config validation succeed.
3. **OmniRoute Compression Pipeline (`~/Omniroute/scripts/container-entrypoint-compat.sh` -> container `omniroute`)**: Compiled-chunk normalization in untracked `scripts/container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`) with `requiredMarkers` verification inside container `omniroute`, keeping `git -C ~/Omniroute status --short` clean of tracked modifications.
4. **Workstation Automation & Knowledge (`~/Developer/scripts/`, `~/.hermes/skills/`, `~/Developer/wiki/` -> Notion)**: Byte-identical script updates to `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh`, followed by idempotent Notion page sync (`sync-notion-knowledge.sh --section entities`).

## Goals / Non-Goals

**Goals:**
- Eliminate the ~38,000-token per-turn MCP schema overhead and 10-second startup wait in Pi v1.4.0 while keeping all non-redundant `mcp-router` tools reachable.
- Eliminate the 108 bogus `(project)` subagents caused by `pi-subagents` scanning `~/Developer/.agents/.skill-snapshots/`.
- Restore authenticated, timeout-bounded `agentmemory` recall/save/observe in Pi without invalidating the provider prompt cache (`cacheRead`) or overwriting Pi 1.4.0's structured `SystemPromptSections`.
- Opt Pi's OmniRoute providers (`omniroute`, `omniroute-anthropic`, `omniroute-responses`) out of OmniRoute's built-in `Memory context:` prompt injection via `"headers": { "x-omniroute-no-memory": "true" }`.
- Prevent OmniRoute's `rtk` engine from running content-based shell filters against non-shell `function_call_output` items (`read`, `glob`, `grep`, `write`, `edit`) over `/v1/responses`.
- Remove all plaintext API keys and broken `"pplx-..."` placeholders from Pi's `mcp.json` and `web-search.json`.

**Non-Goals:**
- Modifying Pi's `defaultProvider` (`omniroute-responses`) or `defaultModel` (`gemini-3.8-flash-high`), or removing existing provider blocks in `~/.pi/agent/models.json`.
- Changing `~/.pi/agent/trust.json`, modifying git-tracked files in `~/Omniroute`, or touching any non-Pi coding agent configuration.

## Decisions

### Decision 1: Use `"exposure": "codemode"` with a Static `description` and `hidden` Desktop Commander Tools in `~/.pi/agent/mcp.json`

- **Choice**: Configure `mcp-router` in `~/.pi/agent/mcp.json` with `"exposure": "codemode"`, a static `"description"` string, `"MCPR_TOKEN": "${MCPR_TOKEN}"`, and `"toolExposure"` mapping all 25 Desktop Commander tools to `"hidden"`, while adding `"defaultTools": ["+codemode", "+tool_search"]` to `~/.pi/agent/settings.json`.
- **Rationale**: In Pi 1.4.0's `dist/extensions/mcp/index.js`, `hasDirectTools(entry)` checks `configuredExposures(entry).has("direct")`. If even one tool is `"direct"`, Pi blocks the first prompt up to `DEFAULT_STARTUP_WAIT_MS` (10,000 ms) waiting for `npx -y @mcp_router/cli@latest connect`. Setting `"exposure": "codemode"` with zero `"direct"` overrides makes `hasDirectTools` `false` (0 ms startup block), removes all 138 MCP tool declarations from the per-turn request payload, keeps the tool list constant for prompt-cache preservation, and provides untruncated `CallToolResult` objects to QuickJS `codemode` scripts. Providing a static `"description"` in `mcp.json` ensures `renderServersSection()` emits the identical `mcp_servers` prompt section before and after background connection, avoiding a Turn-2 system-prompt diff.
- **Alternatives Considered**:
  - *Keep `"exposure": "direct"`*: Rejected — injects 138 tool schemas (~38k tokens) every turn, blocks Turn 1 startup, and duplicates Pi's native tools.
  - *Use `"exposure": "deferred"` without `codemode`*: Rejected — loading tools via `tool_search` mutates the top-level `tools` array on the next turn, busting the prompt cache on custom `openai-responses` providers where `supportsAdditionalTools` is `false`. Enabling both `+codemode` and `+tool_search` in `defaultTools` while defaulting `mcp-router` to `codemode` gives the model zero-cache-bust `codemode` execution by default with `tool_search` available as an opt-in fallback.

### Decision 2: Prune `.skill-snapshots` and `.agents/skills` via `subagents.agentExcludeDirs` and Configure Role Overrides

- **Choice**: Add a `subagents` block in `~/.pi/agent/settings.json` setting `"agentExcludeDirs": ["~/.agents/skills", "~/.agents/.skill-snapshots", "/Users/androidteam/Developer/.agents/skills", "/Users/androidteam/Developer/.agents/.skill-snapshots"]`, `"defaultProvider": "omniroute-responses"`, `"defaultModel": "gemini-3.8-flash-high"`, and role-based `agentOverrides` (`oracle`: `{"model": "omniroute-responses/gemini-4-argon-high", "thinking": "high"}`; `scout`, `researcher`, `reviewer`: `{"model": "omniroute-responses/gemini-3.8-flash-high", "thinking": "medium" | "high" | "xhigh"}`). Omit `projectRootResolution` from `~/.pi/agent/settings.json` because `readProjectRootResolution()` in `pi-subagents/src/agents/agents.js` only reads project-level `.pi/settings.json`.
- **Rationale**: In `pi-subagents` v0.84.0 (`src/agents/agents.js`), `isLegacyAgentSkillPath()` only ignores paths matching `.agents/skills`. Because `sync-workspace-agent-skills.py` maintains skill snapshots under `~/Developer/.agents/.skill-snapshots/{current,previous}/files/<skill>/SKILL.md`, `inspectAgentDefinitionDirectory()` traverses both snapshot trees and registers 108 skill markdown files as `(project)` subagents, which take precedence over builtin agents (`scout`, `worker`, `reviewer`, `oracle`). `agentExcludeDirs` is evaluated in `inspectAgentDefinitionDirectory()` before directory recursion and before `watchPathSignature()` fingerprinting.
- **Alternatives Considered**:
  - *Patch `isLegacyAgentSkillPath()` inside `~/.pi/agent/npm/node_modules/pi-subagents`*: Rejected — `pi update --all` overwrites `node_modules`, whereas `subagents.agentExcludeDirs` in `settings.json` is the official supported configuration surface (`pi-subagents/docs/configuration.md`).

### Decision 3: Resolve `AGENTMEMORY_SECRET` with `~/.agentmemory/.env` Fallback, Bound Timeouts, and Use `promptGuidelines` + Custom Messages in `agentmemory/index.js`

- **Choice**:
  1. Export `AGENTMEMORY_SECRET` in `~/.zshenv` **and** add a fallback helper in `~/.pi/agent/extensions/agentmemory/index.js` that parses `AGENTMEMORY_SECRET` from `~/.agentmemory/.env` when `process.env.AGENTMEMORY_SECRET` is unset, plus a 2,500 ms `AbortSignal.timeout` on `fetch()`.
  2. In `before_agent_start`, push `TOOL_GUIDANCE` into `event.systemPromptOptions.promptGuidelines` (if not already present) **before** any early return so every turn in the session (including custom-message turns) shares identical `promptGuidelines`.
  3. Skip `smart-search` when `event.messageType === "custom"`. When `smart-search` returns results on a user prompt, return `{ message: { customType: "agentmemory-recall", content: recallBlock, display: false } }` instead of concatenating `recallBlock` onto `event.systemPrompt`.
- **Rationale**: Parent harnesses (such as Hermes) strip `*_SECRET` variables from child environments, so relying solely on `process.env.AGENTMEMORY_SECRET` causes silent `HTTP 401` failures. Furthermore, in Pi 1.4.0 (`dist/core/system-prompt.d.ts`), returning `{ systemPrompt }` from `before_agent_start` sets `forceSystemPrompt`, which disables structured `SystemPromptSections` and rewrites byte 0 of the system prompt whenever `recallBlock` changes—invalidating the entire prompt cache on every user turn. Returning `message` appends a hidden transcript entry at the tail of the conversation while keeping the leading system prompt 100% cache-stable.
- **Alternatives Considered**:
  - *Disable automatic pre-prompt recall completely*: Considered, but returning a tail `CustomMessage` only when relevant memories exist preserves automatic recall without busting the prefix cache.

### Decision 4: Preserve OpenAI Responses `function_call` Tool Metadata in OmniRoute via `container-entrypoint-compat.sh`

- **Choice**: Update untracked `~/Omniroute/scripts/container-entrypoint-compat.sh` (and `ensure-muse-wire-compat.sh`) so the compiled `bodyAdapter` chunks (`14211.js`, `41669.js`, `72459.js`, `88137.js`, `98542.js`) attach `c.tool_call_id = k` inside `markCodexResponseEligibility` and the compiled `rtk` chunks (`53846.js`, `72459.js`) scan `Array.isArray(a.input)` for `type === "function_call"` items (`call_id`, `name`, `arguments.command`) into `toolCallLookup` (`m`), verified by `requiredMarkers` in `container-entrypoint-compat.sh`.
- **Rationale**: In `rtk/index.ts` (`53846.js` and `72459.js`), `resolveToolMeta(callId, toolCallLookup)` returns `{ command: null, skipFilters: false }` whenever `callId` is `null` or missing from `toolCallLookup`, assuming an unknown tool call might be a shell command. Because `bodyAdapter` only mapped `RESPONSES_MESSAGE_TYPES` (`message`, `function_call_output`, etc.) and dropped `function_call` items and `call_id`, every Responses API tool output had `callId = null` and `skipFilters = false`. As a result, `read` outputs on files like `settings.json`, `mcp.json`, and `package.json` matched RTK's `npm-audit` and `json-output` filters and lost 80% of their lines. Patching the compiled chunks via `container-entrypoint-compat.sh` fixes the live `omniroute` container immediately while keeping `~/Omniroute`'s git working tree 100% clean (`origin/main`).
- **Alternatives Considered**:
  - *Edit git-tracked `~/Omniroute/open-sse/services/compression/*.ts` on the host*: Rejected — the `omniroute` container runs prebuilt Hub chunks under `/app/.build/next/server/chunks/` (not host `.ts` files), and modifying git-tracked files in `~/Omniroute` breaks the clean-worktree invariant required by `update.sh`.

### Decision 5: Add `"x-omniroute-no-memory": "true"` to OmniRoute Providers in `models.json` and Migrate `web-search.json` to `~/.pi/agent/web-search.json` (`0600`)

- **Choice**:
  1. Keep all 6 existing providers in `~/.pi/agent/models.json`, synchronize `sh/codex-x` `thinkingLevelMap` between `omniroute` and `omniroute-responses`, and add `"headers": { "x-omniroute-no-memory": "true" }` to `omniroute`, `omniroute-anthropic`, and `omniroute-responses`.
  2. Move `~/.pi/web-search.json` (`0644`) to `~/.pi/agent/web-search.json` (`0600`), export `GEMINI_API_KEY` in `~/.zshenv`, replace all literal API keys with `"$EXA_API_KEY"`, `"$BRAVE_SEARCH_API_KEY"`, `"$TAVILY_API_KEY"`, `"$FIRECRAWL_API_KEY"`, and `"$GEMINI_API_KEY"`, remove `"perplexityApiKey": "pplx-..."`, and configure `searchRouting` (`["exa", "brave", "tavily"]`) and `fetchRouting` (`["http", "firecrawl"]`).
- **Rationale**: Per `omniroute-compression-and-routing/spec.md`, requests without `x-omniroute-no-memory: true` receive OmniRoute's built-in `Memory context:` prompt prefix and regex fact extraction, which duplicates Pi's dedicated `agentmemory` extension. Preserving `providers.omniroute` satisfies `coding-cli-provider-registry/spec.md` (`existing providers and defaults are preserved`).

### Decision 6: Create `~/.pi-lens/config.json` with `retain: true` and `requirePreExistingFixes: false`

- **Choice**: Create `~/.pi-lens/config.json` (`0600`) with `contextInjection: { enabled: true, retain: true, requirePreExistingFixes: false }` and `ignore: ["**/.skill-snapshots/**", "**/graphify-out/**", "**/.gitnexus/**", "**/openspec/changes/archive/**"]`.
- **Rationale**: Per `pi-lens/docs/globalconfig.md`, `retain: true` keeps injected diagnostic blocks at a fixed transcript offset across turns so prefix caches remain valid, and `requirePreExistingFixes: false` scopes diagnostic remediation demands to errors introduced by the agent's own edits rather than pre-existing repository issues.

## Risks / Trade-offs

- **[Risk] Hiding Desktop Commander tools in `mcp.json` hides `write_pdf` alongside file/process tools** → **Mitigation**: All 25 Desktop Commander tools are hidden from direct/indirect exposure per spec because Desktop Commander restricts paths to `/Users/androidteam/Developer` and `/Users/androidteam/.hermes` and duplicates Pi's native `read`, `write`, `edit`, and `bash` tools.
- **[Risk] Patching OmniRoute compiled chunks in `container-entrypoint-compat.sh` could fail on future image upgrades if chunk names change** → **Mitigation**: Register explicit `requiredMarkers` in `container-entrypoint-compat.sh` so `update.sh` Gate 4b fails closed if upstream refactors those chunks.
- **[Risk] Removing `~/.pi/agent/install/releases/1.3.0` and `.bak*` files removes in-directory rollback copies** → **Mitigation**: Snapshot all modified and pruned files into `/tmp/pi-optimize-backup/` before deletion, and verify `pi --version` (`1.4.0`), `pi list`, `pi mcp list`, and `pi --list-models` before pruning `releases/1.3.0`.

## Migration Plan

1. **Pre-Flight Backup**: Create `/tmp/pi-optimize-backup/` (`0700`) and copy `~/.zshenv`, `~/.pi/agent/{settings,models,mcp}.json`, `~/.pi/web-search.json`, `~/.pi/agent/extensions/agentmemory/index.js`, `~/.pi/agent/memory/`, `~/.pi/agent/tdt/`, `~/.pi/agent/projects-memory/`, and `/Users/androidteam/Developer/.agentmemory/`.
2. **Credentials & Config Updates**:
   - Update `~/.zshenv` (`0600`) to export `MCPR_TOKEN`, `AGENTMEMORY_SECRET`, and `GEMINI_API_KEY`.
   - Write updated `~/.pi/agent/mcp.json` (`0600`), `~/.pi/agent/settings.json` (`0600`), `~/.pi/agent/models.json` (`0600`), `~/.pi/agent/web-search.json` (`0600`), and `~/.pi-lens/config.json` (`0600`).
   - Update `~/.pi/agent/extensions/agentmemory/index.js`.
3. **OmniRoute Compression Fix**:
   - Update `~/Omniroute/scripts/container-entrypoint-compat.sh` (`ensure-muse-wire-compat.sh`) with the OpenAI Responses `function_call` -> `tool_call_id` / `toolCallLookup` chunk rules and `requiredMarkers`, execute `/app/container-entrypoint-compat.sh --patch-only` inside container `omniroute`, restart `omniroute`, and verify health (`docker inspect omniroute`) plus a live `/v1/responses` file-read preservation check.
4. **Hygiene, Automation & Docs**:
   - Prune `~/.pi/agent/install/releases/1.3.0`, `.bak*` files, orphaned `pi-hermes-memory` dirs, `/Users/androidteam/Developer/.agentmemory`, and truncate `~/.pi-lens/{latency,sessionstart}.log`.
   - Update `workstation-daily-update.sh` (both copies) to `pi:Pi:update --all`.
   - Update `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` and `~/Developer/wiki/entities/pi.md`, then sync to Notion (`sync-notion-knowledge.sh --section entities`).
5. **Rollback**: Restore files from `/tmp/pi-optimize-backup/` and restart container `omniroute` if any verification gate fails.
