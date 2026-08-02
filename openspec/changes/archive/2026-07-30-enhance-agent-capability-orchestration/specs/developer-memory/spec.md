## MODIFIED Requirements

### Requirement: Agentmemory server as developer-memory layer

The project SHALL adopt agentmemory as the developer-memory layer and SHALL
verify both its loopback server and its configured agent integrations before
claiming the memory capability is active. The orchestration workflow SHALL use
memory for prior decisions, lessons, and session context, but SHALL NOT treat
memory as authoritative over OpenSpec requirements or source code. Tool-surface
verification MUST derive its expected set from the selected
`AGENTMEMORY_TOOLS` mode and reviewed upstream version.

#### Scenario: Agentmemory server is installed locally

- **WHEN** a developer runs the supported bootstrap and start commands
- **THEN** the server starts on the configured loopback REST/MCP and viewer
  endpoints with the selected feature flags, and diagnostics report zero red
  health rows

#### Scenario: Agentmemory full tool surface is reachable

- **WHEN** an agent connects through MCP after the server is healthy
- **THEN** the visible tool count matches the selected `AGENTMEMORY_TOOLS`
  mode, and a save/search round trip succeeds without exposing credentials

#### Scenario: Agentmemory core tool surface is selected

- **WHEN** the reviewed configuration selects the core tool profile
- **THEN** health requires only the version-documented core tools and reports
  the selected mode rather than misclassifying the intentional reduction

#### Scenario: Agentmemory server is unavailable

- **WHEN** MCP wiring or lifecycle hooks exist but the loopback health endpoint
  is unreachable
- **THEN** the memory capability is unavailable, context injection and capture
  are not claimed, and other repository verification remains usable

#### Scenario: Disposable round-trip evidence is cleaned up

- **WHEN** implementation-readiness verification creates a run-tagged memory
- **THEN** the exact record is retrieved, deleted through the supported
  governance path, and its deletion or audit result is retained without
  leaving an unclassified durable test record

#### Scenario: Repeated health verification is idempotent

- **WHEN** the same health profile is run repeatedly
- **THEN** each run uses a unique probe identity, cleans up its own record, and
  does not change existing durable memories or duplicate agent wiring

#### Scenario: Agentmemory is wired to Cursor

- **WHEN** Cursor starts with the agentmemory MCP server configured
- **THEN** its tool palette shows the selected agentmemory surface and the
  health report records the client identity

#### Scenario: Agentmemory is wired to Claude Code

- **WHEN** Claude Code starts with the agentmemory hooks configured
- **THEN** lifecycle hooks fire on the supported session and tool events and
  memory results retain the correct agent identity

#### Scenario: Agentmemory is wired to Codex CLI

- **WHEN** Codex CLI or Desktop starts with the agentmemory MCP and mirrored
  hooks configured
- **THEN** the supported session, prompt, tool, compaction, and stop events
  are wired and health evidence distinguishes hook configuration from live
  server reachability

#### Scenario: Agentmemory is wired to OpenCode or pi

- **WHEN** OpenCode or pi starts with its configured agentmemory integration
- **THEN** the selected memory tools or extension hooks are discoverable and
  the client identity is recorded without changing application dependencies

#### Scenario: Memory is used as contextual evidence

- **WHEN** an agent retrieves a prior decision or lesson for an active change
- **THEN** it records the memory reference as contextual evidence and follows
  the current OpenSpec and source-code contract when they disagree

#### Scenario: Optional LLM features are unavailable

- **WHEN** Ollama or another optional summarization provider is not reachable
- **THEN** zero-LLM capture and retrieval health remain independently
  reportable and no implementation-readiness claim requires optional
  compression or summarization

### Requirement: No Go service code is modified

The developer-memory integration SHALL NOT modify any Go service code, package
structure, or dependency graph. The integration is entirely in developer
tooling.

#### Scenario: Go dependency graph is unchanged

- **WHEN** `go list -m all` runs against the `platform/` module
- **THEN** no agentmemory package appears in the dependency closure
