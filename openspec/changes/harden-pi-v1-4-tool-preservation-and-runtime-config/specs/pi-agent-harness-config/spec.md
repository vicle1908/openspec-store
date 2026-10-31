# pi-agent-harness-config Specification

## ADDED Requirements

### Requirement: GitNexus Auto-Augment Opt-Out and Cache-Safe System Prompt Interception

The Pi GitNexus configuration `~/.pi/pi-gitnexus.json` SHALL exist with mode `0600` and set `"autoAugment": false` so `tool_result` hooks do not spawn `gitnexus augment` subprocesses or append empty banners, and `~/.pi/agent/extensions/agentmemory/index.js` SHALL intercept static suffix assignments to `event.systemPromptOptions.forceSystemPrompt` during `before_agent_start` and convert them into `promptGuidelines` entries so `forceSystemPrompt` remains `undefined`.

#### Scenario: Read and search tool outputs are not polluted with empty GitNexus Augment banners
- **WHEN** `~/.pi/pi-gitnexus.json` is inspected and `read`, `grep`, `find`, or `bash` is executed in `/Users/androidteam/Developer`
- **THEN** `~/.pi/pi-gitnexus.json` SHALL have mode `0600` and declare `{"autoAugment": false}`
- **AND** `pi-gitnexus` SHALL NOT spawn `gitnexus augment` on `tool_result` events or append `GitNexus Augment (1.6.12)` banners while keeping explicit `gitnexus_*` tools available

#### Scenario: Static before_agent_start systemPrompt suffixes convert to promptGuidelines without setting forceSystemPrompt
- **WHEN** `emitBeforeAgentStart` executes in `/Users/androidteam/Developer` with both `agentmemory` and `pi-gitnexus` loaded
- **THEN** `event.systemPromptOptions.forceSystemPrompt` SHALL remain `undefined` after all `before_agent_start` handlers complete
- **AND** `event.systemPromptOptions.promptGuidelines` SHALL contain both the `agentmemory` tool guidance and the `[GitNexus active]` guidance

## MODIFIED Requirements

### Requirement: Core Settings and Models Schema Conformance and OmniRoute Memory Opt-Out

The Pi Coding Agent configuration files `~/.pi/agent/settings.json` and `~/.pi/agent/models.json` SHALL declare their official `pi.dev` JSON schemas, SHALL remain mode `0600`, SHALL set `"transport": "auto"`, `"defaultTools": ["+codemode", "+tool_search"]`, and `"skills": ["!**/cli-*", "!**/omni-*"]`, SHALL send `"x-omniroute-no-memory": "true"` on all OmniRoute providers, SHALL configure `"supportsMidConvoSystemMessages": true` on all 6 custom providers (`"supportsLongCacheRetention": true` on `omniroute-responses`), and SHALL trust `/Users/androidteam/Omniroute` in `~/.pi/agent/trust.json`.

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

### Requirement: Subagent Discovery Exclusion Boundaries and Role Routing

The `subagents` configuration in `~/.pi/agent/settings.json` SHALL exclude skill and snapshot directories (`~/.agents/skills`, `~/.agents/.skill-snapshots`, `/Users/androidteam/Developer/.agents/skills`, `/Users/androidteam/Developer/.agents/.skill-snapshots`) via `agentExcludeDirs`, and SHALL configure role-based `agentOverrides` for `scout`, `researcher`, `reviewer`, `oracle`, and `worker` using explicit `model`, `thinking`, and `"advertise": true` fields while preserving the default provider and model.

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

The `pi-web-access` configuration SHALL reside at `~/.pi/agent/web-search.json` with mode `0600` (removing legacy `~/.pi/web-search.json`), SHALL reference API keys exclusively via `"$ENV_VAR"` indirection backed by `~/.zshenv` with no `"pplx-..."` placeholder, SHALL omit `"provider"` / `"searchProvider"` so `getConfiguredSearchRouting()` activates `searchRouting`, SHALL set `"firecrawlBaseUrl": "https://api.firecrawl.dev"` so Firecrawl is available in `fetchRouting`, and SHALL set `"workflow": "none"` and `"searchModel": "gemini-3.6-flash"`.

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
