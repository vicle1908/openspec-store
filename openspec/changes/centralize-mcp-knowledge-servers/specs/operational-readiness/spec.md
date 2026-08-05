## MODIFIED Requirements

### Requirement: Agent configs SHALL be wired for all supported agents

The platform SHALL provide properly configured agent configuration files for all supported AI coding agents (Claude via `.claude/settings.json`, Cursor via `.cursor/mcp.json`, Codex, KiloCode, Kiro, Factory, OpenCode, Zed, Kimi, Antigravity, and Hermes where installed). Each supported MCP client SHALL use MCP Router as the single client-facing gateway for GitNexus, Graphify, and AgentMemory. Client configuration MUST NOT additionally register those same knowledge servers directly unless a documented, time-bounded compatibility exception identifies the owner, reason, expiry, and rollback. Configurations MUST remain synchronized with the platform topology and MUST NOT contain hardcoded secrets or credentials.

#### Scenario: Claude settings reference correct MCP servers

- **WHEN** a developer opens the project with Claude Code
- **THEN** Claude's effective MCP configuration points to the authorized MCP Router endpoint or bridge
- **AND** no duplicate direct GitNexus, Graphify, or AgentMemory MCP registration is active outside an approved compatibility exception

#### Scenario: Cursor MCP config includes all required tools

- **WHEN** a developer opens the project with Cursor
- **THEN** Cursor reaches all required platform-development tools through the authorized MCP Router connection
- **AND** the effective configuration contains no duplicate direct GitNexus, Graphify, or AgentMemory server

#### Scenario: Effective client topology is audited

- **WHEN** the operator runs the MCP topology diagnostic
- **THEN** it inventories every supported client configuration, MCP Router server, bridge process, and direct GitNexus, Graphify, and AgentMemory process family
- **AND** it distinguishes the expected one bridge per active client from duplicate child knowledge-server processes
- **AND** it emits only redacted paths, server names, process identities, counts, and health states

#### Scenario: Duplicate direct knowledge server is detected

- **WHEN** a supported client config or process tree contains a direct GitNexus, Graphify, or AgentMemory MCP server in addition to MCP Router
- **THEN** readiness fails and identifies the owning client and duplicate server class without printing credentials or command-line secret values
- **AND** no automatic deletion or process termination occurs during diagnosis

#### Scenario: Live client cutover is authorized

- **WHEN** reviewed source changes, backups, synthetic migration, restore rehearsal, and an exact redacted cutover plan have passed
- **THEN** an operator may issue execution approval bound to the plan digest, client inventory, configuration fingerprints, process owners, and maintenance window
- **AND** stale or changed inputs invalidate that approval before mutation

#### Scenario: Client cutover succeeds

- **WHEN** the approved live cutover removes duplicate direct registrations and restarts affected clients
- **THEN** each required client discovers GitNexus, Graphify, and AgentMemory through MCP Router
- **AND** no duplicate child knowledge-server process family remains after old client sessions exit
- **AND** client hooks, skills, unrelated MCP servers, credentials, sessions, and local indexes remain intact

#### Scenario: Client cutover fails

- **WHEN** any required client cannot discover or call its required router-exposed knowledge tools after cutover
- **THEN** maintenance remains active and the operator restores the exact backed-up client configuration for the affected scope
- **AND** the run records the failure and rollback outcome without exposing secrets
