# pi-agent-harness-config Specification

## Purpose

Defines the runtime configuration, schema validation, OmniRoute memory opt-out headers, native MCP exposure, subagent discovery boundaries, web-access credential indirection, Pi-Lens cache-preserving diagnostics, and artifact hygiene invariants for the Pi Coding Agent (`~/.pi/agent/` and `~/.pi-lens/`).

## Requirements

### Requirement: Core Settings and Models Schema Conformance and OmniRoute Memory Opt-Out

The Pi files `~/.pi/agent/settings.json` and `~/.pi/agent/models.json` SHALL declare `pi.dev` JSON schemas, remain mode `0600`, set `"transport": "auto"`, `"defaultTools": ["+codemode", "+tool_search"]`, and `"skills": ["!**/cli-*", "!**/omni-*"]`, send `"x-omniroute-no-memory": "true"` on OmniRoute providers, enable `"supportsMidConvoSystemMessages": true` on all 6 providers (`"supportsLongCacheRetention": true` on `omniroute-responses`), and trust `/Users/androidteam/Omniroute`.

#### Scenario: Settings and models files validate against official schemas and permissions
- **WHEN** `~/.pi/agent/settings.json`, `~/.pi/agent/models.json`, and `~/.pi/agent/trust.json` are inspected
- **THEN** `settings.json` and `models.json` SHALL have filesystem permissions `0600`
- **AND** `settings.json` SHALL declare `"$schema": "https://pi.dev/schemas/settings.schema.json"` with `"transport": "auto"`, `"defaultTools": ["+codemode", "+tool_search"]`, and `"skills": ["!**/cli-*", "!**/omni-*"]` (excluding the 44 non-symlinked OmniRoute internal CLI skills from `~/.agents/skills/` without deleting files on disk)
- **AND** `models.json` SHALL declare `"$schema": "https://pi.dev/schemas/models.schema.json"`
- **AND** `trust.json` SHALL map both `"/Users/androidteam/Developer": true` and `"/Users/androidteam/Omniroute": true`
- **AND** `settings.json` SHALL NOT contain the redundant `"extensions": ["+builtin:mcp"]` override

#### Scenario: OmniRoute providers opt out of gateway memory injection and thinking maps match declared models
- **WHEN** `modelThinkingLevels` in `~/.pi/agent/settings.json` and `providers` in `~/.pi/agent/models.json` are inspected
- **THEN** every `provider/modelId` key in `modelThinkingLevels` SHALL resolve to an existing model in `models.json` (replacing stale `"cockpit/gpt-5.6-sol"` with `"cockpit/codex-x"`)
- **AND** `omniroute`, `omniroute-anthropic`, and `omniroute-responses` in `models.json` SHALL remain present and each SHALL declare `"headers": { "x-omniroute-no-memory": "true" }`
- **AND** `omniroute-responses` SHALL declare `"compat": { "supportsLongCacheRetention": true, "supportsMidConvoSystemMessages": true }` and `cockpit`, `omniroute`, `phanmemvip`, `shopapikey`, and `omniroute-anthropic` SHALL include `"supportsMidConvoSystemMessages": true` in their `compat` blocks
- **AND** `sh/codex-x` in `providers.omniroute` and `providers.omniroute-responses` SHALL have identical `thinkingLevelMap` definitions

#### Scenario: Compaction token budgets protect 1M-context models from output overflow
- **WHEN** `compaction` in `~/.pi/agent/settings.json` is inspected
- **THEN** `compaction.enabled` SHALL be `true`, `compaction.reserveTokens` SHALL be `65536`, and `compaction.keepRecentTokens` SHALL be `40000`

### Requirement: Native MCP Codemode Exposure and Credential Indirection

The user-level MCP configuration `~/.pi/agent/mcp.json` SHALL configure `mcp-router` with `"exposure": "codemode"`, a static non-empty `"description"`, environment-variable credential indirection (`"${MCPR_TOKEN}"` backed by `~/.zshenv`), and `"toolExposure"` rules that hide Desktop Commander tools duplicating Pi's built-in file and shell primitives.

#### Scenario: MCP router connects in codemode without blocking initial prompt or leaking inline tokens
- **WHEN** `~/.pi/agent/mcp.json` is inspected and `pi mcp list` is executed
- **THEN** `~/.pi/agent/mcp.json` SHALL have mode `0600` and reference `"MCPR_TOKEN": "${MCPR_TOKEN}"` with no literal `mcpr_` token string on disk
- **AND** `mcp-router` SHALL report `"exposure": "codemode"` with a static `"description"` string
- **AND** zero tools on `mcp-router` SHALL have `"direct"` exposure so `hasDirectTools` is `false` at session start

#### Scenario: Redundant Desktop Commander tools are hidden while knowledge and search tools remain reachable
- **WHEN** `mcp-router` `toolExposure` in `~/.pi/agent/mcp.json` is evaluated
- **THEN** all 25 Desktop Commander file, process, search, and config tools (`read_file`, `read_multiple_files`, `write_file`, `write_pdf`, `create_directory`, `list_directory`, `move_file`, `get_file_info`, `edit_block`, `start_search`, `get_more_search_results`, `stop_search`, `list_searches`, `start_process`, `read_process_output`, `interact_with_process`, `force_terminate`, `list_sessions`, `list_processes`, `kill_process`, `get_config`, `set_config_value`, `get_usage_stats`, `get_recent_tool_calls`, `give_feedback_to_desktop_commander`) SHALL be set to `"hidden"`
- **AND** non-hidden `mcp-router` tools (`wiki_*`, `resolve-library-id`, `query-docs`, `graphify`, `gitnexus`, `agentmemory`, `exa`, `brave`, `tavily`) SHALL remain reachable via `codemode` and `tool_search`

#### Scenario: Missing MCPR_TOKEN environment variable fails closed
- **WHEN** `MCPR_TOKEN` is unset in the environment during an isolated connection probe
- **THEN** `~/.pi/agent/mcp.json` SHALL NOT fall back to an inline hardcoded token

### Requirement: Subagent Discovery Exclusion Boundaries and Role Routing

The `subagents` configuration in `~/.pi/agent/settings.json` SHALL exclude skill and snapshot directories (`~/.agents/skills`, `~/.agents/.skill-snapshots`, `/Users/androidteam/Developer/.agents/skills`, `/Users/androidteam/Developer/.agents/.skill-snapshots`) via `agentExcludeDirs`, and SHALL configure role-based `agentOverrides` for `scout`, `researcher`, `reviewer`, `oracle`, and `worker` with explicit `model`, `thinking`, and `"advertise": true` fields.

#### Scenario: Skill snapshots and skill directories are excluded from subagent discovery
- **WHEN** `discoverAgents("/Users/androidteam/Developer", "both")` or `subagent({ action: "list" })` is executed from `/Users/androidteam/Developer`
- **THEN** zero skills or skill snapshots from `.agents/skills` or `.agents/.skill-snapshots` (such as `agent-onboarding`, `bright-data-mcp`, or `ponytail-audit`) SHALL appear as `(project)` subagents
- **AND** all 13 builtin subagents (`claude-code`, `claude-code-writer`, `codex-exec`, `codex-exec-writer`, `cursor-agent`, `cursor-agent-writer`, `delegate`, `evidence-auditor`, `oracle`, `researcher`, `reviewer`, `scout`, `worker`) SHALL remain discoverable and visible in `subagent({ action: "list" })` without shadowing or RTK line stripping

#### Scenario: Subagent role overrides route specialist agents without changing startup defaults
- **WHEN** `subagents` in `~/.pi/agent/settings.json` is inspected
- **THEN** `defaultProvider` SHALL be `"omniroute-responses"` and `defaultModel` SHALL be `"gemini-3.8-flash-high"`
- **AND** `agentOverrides.oracle` SHALL set `"model": "omniroute-responses/gemini-4-argon-high"`, `"thinking": "high"`, and `"advertise": true`
- **AND** `scout`, `researcher`, `reviewer`, and `worker` SHALL set `"model": "omniroute-responses/gemini-3.8-flash-high"`, `"advertise": true`, and explicit `"thinking"` levels (`"medium"`, `"high"`, `"xhigh"`, and `"high"`)

### Requirement: Pi Web Access Credential Indirection and Multi-Provider Routing

The `pi-web-access` configuration SHALL reside at `~/.pi/agent/web-search.json` (`0600`, removing `~/.pi/web-search.json`), reference API keys via `"$ENV_VAR"` indirection backed by `~/.zshenv` without `"pplx-..."` placeholders, omit `"provider"` / `"searchProvider"` so `getConfiguredSearchRouting()` activates `searchRouting`, and set `"firecrawlBaseUrl": "https://api.firecrawl.dev"`, `"workflow": "none"`, and `"searchModel": "gemini-3.6-flash"`.

#### Scenario: Web search config uses agent directory path, 0600 mode, and environment indirection
- **WHEN** `~/.pi/agent/web-search.json` and `~/.pi/web-search.json` are inspected
- **THEN** `~/.pi/agent/web-search.json` SHALL exist with mode `0600` and `~/.pi/web-search.json` SHALL NOT exist
- **AND** `exaApiKey`, `braveApiKey`, `tavilyApiKey`, `firecrawlApiKey`, and `geminiApiKey` SHALL use `"$EXA_API_KEY"`, `"$BRAVE_SEARCH_API_KEY"`, `"$TAVILY_API_KEY"`, `"$FIRECRAWL_API_KEY"`, and `"$GEMINI_API_KEY"` respectively
- **AND** no literal API keys or `"pplx-..."` placeholder strings SHALL exist in `~/.pi/agent/web-search.json`

#### Scenario: Multi-provider search and fetch routing fallback order is configured
- **WHEN** `getConfiguredSearchRouting()` and `isFirecrawlAvailable()` in `pi-web-access` are evaluated against `~/.pi/agent/web-search.json`
- **THEN** `"provider"` and `"searchProvider"` SHALL be absent from `~/.pi/agent/web-search.json` so `getConfiguredSearchRouting()` returns `{ providers: ["exa", "brave", "tavily"], fallbackOn: ["transient", "quota", "network", "invalid-response"] }`
- **AND** `"firecrawlBaseUrl"` SHALL be `"https://api.firecrawl.dev"` so `isFirecrawlAvailable()` returns `true` for `fetchRouting.providers: ["http", "firecrawl"]`
- **AND** `"workflow"` SHALL be `"none"` and `"searchModel"` SHALL be `"gemini-3.6-flash"`

### Requirement: Pi-Lens Global Cache-Stable Context Injection and Scope Boundaries

The global Pi-Lens configuration `~/.pi-lens/config.json` SHALL exist with mode `0600`, SHALL enable `contextInjection.retain` (`true`) for prompt-cache stability, SHALL disable `contextInjection.requirePreExistingFixes` (`false`) to prevent out-of-scope fix demands, and SHALL exclude snapshot, graph, and archive trees via `ignore`.

#### Scenario: Pi-Lens effective configuration resolves global cache-stable and scope-bounded settings
- **WHEN** `effective_config` is invoked or `~/.pi-lens/config.json` is inspected
- **THEN** `~/.pi-lens/config.json` SHALL have mode `0600` and declare `"$schema": "https://raw.githubusercontent.com/apmantza/pi-lens/master/docs/schema/pi-lens-config-v1.json"`
- **AND** `contextInjection.enabled` SHALL be `true`, `contextInjection.retain` SHALL be `true`, and `contextInjection.requirePreExistingFixes` SHALL be `false`
- **AND** `ignore` SHALL include `"**/.skill-snapshots/**"`, `"**/graphify-out/**"`, `"**/.gitnexus/**"`, and `"**/openspec/changes/archive/**"`

### Requirement: Pi Release Hygiene, Package Update Coverage, and Documentation Parity

The `~/.pi/agent/` directory SHALL retain only the active managed release (`1.4.0`) without stale `.bak*` or orphaned `pi-hermes-memory` directories, `workstation-daily-update.sh` SHALL update both Pi core and managed packages via `pi update --all` and truncate `~/.pi-lens/*.log` files exceeding 5 MB (`5242880` bytes), and the Hermes Pi skill and Notion-synced Wiki entity SHALL match the live Pi v1.4.0 configuration.

#### Scenario: Superseded releases, backup files, and orphaned memory directories are absent
- **WHEN** `~/.pi/agent/` is inspected
- **THEN** `~/.pi/agent/install/releases/1.3.0`, `~/.pi/agent/skills.bak-20261004164935`, `~/.pi/agent/backups`, `~/.pi/agent/models.json.bak*`, `~/.pi/agent/settings.json.bak*`, `~/.pi/agent/memory`, `~/.pi/agent/tdt`, and `~/.pi/agent/projects-memory` SHALL NOT exist
- **AND** `/Users/androidteam/Developer/.agentmemory` SHALL NOT exist

#### Scenario: Workstation daily update script invokes pi update --all and maintains mirror parity
- **WHEN** `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh` are inspected
- **THEN** `AGENT_CLI_COVERED` SHALL specify `pi:Pi:update --all`
- **AND** the script SHALL truncate any `~/.pi-lens/*.log` file whose size exceeds `5242880` bytes (5 MB)
- **AND** both script files SHALL have identical SHA-256 digests

#### Scenario: Hermes Pi orchestration skill and Wiki/Notion documentation reflect Pi v1.4.0
- **WHEN** `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` and `~/Developer/wiki/entities/pi.md` are inspected
- **THEN** both documents SHALL reference Pi `1.4.0`, binary `~/.pi/agent/bin/pi`, default model `omniroute-responses/gemini-3.8-flash-high`, and built-in MCP `"exposure": "codemode"`
- **AND** `wiki/entities/pi.md` SHALL be synchronized to Notion page `3efc4b21-deb4-8129-b9c3-d7c22a453212`

### Requirement: GitNexus Auto-Augment Opt-Out and Cache-Safe System Prompt Interception

The Pi GitNexus config `~/.pi/pi-gitnexus.json` SHALL exist with mode `0600` and set `"autoAugment": false`, and `~/.pi/agent/extensions/agentmemory/index.js` SHALL intercept only the exact `[GitNexus active]` suffix on `event.systemPromptOptions.forceSystemPrompt` into `promptGuidelines` (preserving child subagent boundary prompts) and skip `smart-search` and `observe` network calls inside child subagents.

#### Scenario: Read and search tool outputs are not polluted with empty GitNexus Augment banners
- **WHEN** `~/.pi/pi-gitnexus.json` is inspected and `read`, `grep`, `find`, or `bash` is executed in `/Users/androidteam/Developer`
- **THEN** `~/.pi/pi-gitnexus.json` SHALL have mode `0600` and declare `{"autoAugment": false}`
- **AND** `pi-gitnexus` SHALL NOT spawn `gitnexus augment` on `tool_result` events or append `GitNexus Augment (1.6.12)` banners while keeping explicit `gitnexus_*` tools available

#### Scenario: Exact GitNexus active suffix converts to promptGuidelines while child subagent boundary prompts and network isolation hold
- **WHEN** `emitBeforeAgentStart` executes in `/Users/androidteam/Developer` with both `agentmemory` and `pi-gitnexus` loaded
- **THEN** `event.systemPromptOptions.forceSystemPrompt` SHALL remain `undefined` when `pi-gitnexus` appends the `[GitNexus active]` suffix, and `event.systemPromptOptions.promptGuidelines` SHALL contain both the `agentmemory` tool guidance and the `[GitNexus active]` guidance
- **AND** when a child subagent handler assigns a replacement `forceSystemPrompt` containing `<active_agent` or Subagent Execution Boundary instructions, `forceSystemPrompt` SHALL be preserved unchanged
- **AND** when `process.env.PI_SUBAGENT_CHILD` or `ctx.sessionManager.getHeader()?.parentSession` is present, `agentmemory` SHALL still push `TOOL_GUIDANCE` into `promptGuidelines` but SHALL skip `smart-search` and `observe` network calls
