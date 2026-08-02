## ADDED Requirements

### Requirement: Install agentmemory runtime
The workspace SHALL provide a working global `agentmemory` CLI and MCP shim.

#### Scenario: CLI and server are available
- **WHEN** an agent runs `agentmemory --version`
- **THEN** the version SHALL be at least `0.9.24`
- **AND** `agentmemory` SHALL start a healthy server on `http://localhost:3111`
- **AND** the viewer SHALL be reachable on `http://localhost:3113`

#### Scenario: Demo proves recall
- **WHEN** an agent runs `agentmemory demo`
- **THEN** demo sessions and observations SHALL be stored
- **AND** demo searches SHALL return relevant results


### Requirement: Persist agentmemory runtime startup
The agentmemory REST worker SHALL start automatically for the user session.

#### Scenario: LaunchAgent is loaded
- **WHEN** launchd is inspected for `com.tdt.agentmemory`
- **THEN** the service SHALL be loaded under the current GUI user domain
- **AND** it SHALL run `source ~/.tdt/.env && exec ~/.npm-global/bin/agentmemory`
- **AND** `agentmemory status` SHALL report `v0.9.24` and healthy status

#### Scenario: Logs are available
- **WHEN** the LaunchAgent writes stdout or stderr
- **THEN** logs SHALL be stored under `~/.agentmemory/launchd-stdout.log` and `~/.agentmemory/launchd-stderr.log`

### Requirement: Configure TDT providers
The runtime SHALL use TDT-standard providers for LLM and embeddings.

#### Scenario: OmniRoute and Ollama are configured
- **WHEN** agentmemory starts after `source ~/.tdt/.env`
- **THEN** the LLM provider SHALL use OmniRoute with `ai/deepseek-v4-pro[1m]`
- **AND** embeddings SHALL use local Ollama `nomic-embed-text`
- **AND** embedding vectors SHALL have 768 dimensions

#### Scenario: Lifecycle flags are enabled
- **WHEN** configuration is inspected
- **THEN** consolidation SHALL be enabled
- **AND** graph extraction SHALL be enabled
- **AND** the decay threshold SHALL be 30 days
- **AND** search weights SHALL be BM25 `0.4`, vector `0.6`, graph `0.2`

### Requirement: Wire supported agents
The workspace SHALL wire agentmemory into Claude Code, Codex, and pi.

#### Scenario: Claude Code is wired
- **WHEN** Claude Code reads user configuration
- **THEN** `mcpServers.agentmemory` SHALL point to `@agentmemory/mcp`
- **AND** Claude Code hooks SHALL point to installed agentmemory hook scripts

#### Scenario: Codex is wired
- **WHEN** Codex reads user configuration
- **THEN** `[mcp_servers.agentmemory]` SHALL point to `@agentmemory/mcp`
- **AND** global Codex hooks SHALL point to installed agentmemory hook scripts

#### Scenario: pi is wired
- **WHEN** pi reads `~/.pi/agent/settings.json`
- **THEN** the `~/.pi/agent/extensions/agentmemory` extension SHALL be registered
- **AND** the extension files SHALL exist locally

### Requirement: Expose memory tools
The MCP shim SHALL expose memory tools to connected agents.

#### Scenario: MCP tool list is available
- **WHEN** an MCP client calls `tools/list`
- **THEN** agentmemory SHALL return the current 53 MCP tools
- **AND** the list SHALL include `memory_smart_search`, `memory_save`, `memory_sessions`, `memory_export`, `memory_audit`, and `memory_governance_delete`

#### Scenario: Save and search work
- **WHEN** an agent saves a verification memory
- **THEN** `memory_smart_search` SHALL return that memory for a relevant query
- **AND** `memory_export` SHALL include persisted sessions, observations, and memories

### Requirement: Capture lifecycle observations
Configured hooks SHALL capture lifecycle and tool-use observations without blocking agent work.

#### Scenario: Hook scripts execute successfully
- **WHEN** each configured hook script receives a valid payload
- **THEN** it SHALL exit with status 0 within 5 seconds
- **AND** observations SHALL appear in agentmemory via the API or viewer

#### Scenario: Test Claude session is captured
- **WHEN** a short Claude Code session runs in the workspace
- **THEN** agentmemory SHALL record at least one observation for that session

### Requirement: Verify performance and monitoring
The local runtime SHALL meet baseline performance checks.

#### Scenario: Runtime is responsive
- **WHEN** health and search checks run locally
- **THEN** health SHALL be `healthy`
- **AND** search p50 latency SHALL be under 20ms for the verification query
- **AND** viewer p50 load SHALL be under 2 seconds with more than 100 observations

#### Scenario: Operational state is inspectable
- **WHEN** an agent checks status and audit data
- **THEN** `agentmemory status` SHALL show session and observation counts
- **AND** `memory_audit` SHALL return recent audit entries
- **AND** durable agentmemory state SHALL exist under `~/.agentmemory` and iii-engine state

### Requirement: Support historical import and governance
The integration SHALL support importing prior Claude Code transcripts and governing stored memory.

#### Scenario: Historical sessions import
- **WHEN** `agentmemory import-jsonl` runs against Claude Code transcripts
- **THEN** imported sessions SHALL appear in status and the viewer Replay UI

#### Scenario: Governance delete works
- **WHEN** a disposable memory is saved then deleted via `memory_governance_delete`
- **THEN** the delete operation SHALL report success
- **AND** MCP calls SHALL pass `memoryIds` (supported as comma-separated string or array) rather than a single `id` field

#### Scenario: Slot lifecycle works
- **WHEN** slot APIs are exercised with create/get/append/replace/delete
- **THEN** each operation SHALL succeed with expected state transitions
- **AND** deleted slots SHALL return `success=false` with `slot not found`

#### Scenario: Diagnostic warnings are actionable
- **WHEN** `memory_diagnose` reports fixable warnings (for example project-scope coverage)
- **THEN** the warning SHALL include an explicit remediation path
- **AND** `memory_heal` dry-run SHALL execute successfully without mutating state
