## MODIFIED Requirements

### Requirement: Deterministic instruction precedence

The guidance model SHALL apply broad repository instructions before the closest
applicable scoped instructions. A direct user instruction MUST take precedence
over project guidance, and the orchestration workflow MUST route evidence
according to the authority boundaries defined by the agent-capability-
orchestration capability. Tool routing is advisory and MUST NOT grant mutation
authority, bypass the closest scoped guide, or replace a required repository
verification command.

#### Scenario: Service work receives layered guidance

- **WHEN** an agent starts work under `services/<service>/`
- **THEN** the effective project chain contains the outer root guide followed
  by `services/AGENTS.md`, and orchestration queries are scoped to that service

#### Scenario: Independent repository work receives local guidance

- **WHEN** an agent opens `mcp-router/` as its Git project
- **THEN** its local guide is available and orchestration results preserve the
  nested root instead of inheriting unrelated outer scope

#### Scenario: User direction conflicts with a guide

- **WHEN** an explicit user instruction conflicts with a project guide without
  violating a higher-level safety policy
- **THEN** the agent follows the user instruction, reports any skipped check,
  and records the deviation as evidence rather than silently changing policy

#### Scenario: A routed tool is unavailable

- **WHEN** guidance routes a question to an unavailable knowledge or memory
  tool
- **THEN** the agent uses bounded repository search and direct source
  inspection, reports the missing specialized evidence, and preserves the
  governing instruction chain

### Requirement: MCP health claims require live evidence

The MCP Router and agent guidance SHALL require end-to-end verification before
an agent reports GitNexus, Graphify, agentmemory, or MCP Router availability.
Verification MUST cover configured identity, process/listener state where
applicable, authentication, handshake, and tool/resource discovery. A
configuration file, process restart, or partial tool list MUST NOT establish a
healthy claim. Evidence MUST match the current source identity and remain
within the selected profile's freshness boundary.

#### Scenario: MCP availability is confirmed

- **WHEN** an agent reports an MCP-backed capability as usable
- **THEN** the report is based on a successful live handshake and tool or
  resource discovery in addition to configuration and process checks
- **AND** the evidence names the probed server, root, tool/resource surface,
  duration, and source identity

#### Scenario: Only the process restarts

- **WHEN** an MCP server restarts but authenticated initialization or discovery
  has not succeeded
- **THEN** the agent reports verification as incomplete or failed rather than
  declaring the router or knowledge tool usable

#### Scenario: Agentmemory exposes a reduced tool set

- **WHEN** the MCP bridge exposes fewer tools than the selected agentmemory
  mode requires
- **THEN** the agent reports the memory capability as degraded and does not
  claim that context injection or durable recall is active

#### Scenario: Live evidence belongs to an older source state

- **WHEN** an MCP health report was produced for another commit or dirty-state
  fingerprint
- **THEN** the agent reports it as stale evidence and does not reuse it for the
  current implementation-readiness claim
