## Purpose

This specification defines requirements for Integration Guide.

## Requirements

### Requirement: Supported dependency baseline

The integration guide SHALL document and verify the reviewed framework family.

#### Scenario: Dependency verification

- **WHEN** the harness environment is synchronized
- **THEN** it SHALL use `uv sync --frozen`
- **AND** the version probe SHALL report Pydantic AI 2.18.0, Harness 0.11.0, Monty 0.0.19, and LangGraph 1.2.9

### Requirement: Framework prerequisite verification

The guide SHALL require the stabilization and convergence contract suites before harness implementation or release.

#### Scenario: Consumer readiness

- **WHEN** an operator prepares the harness
- **THEN** the documented checks SHALL verify typed SDK composition, native deferred continuation, Hooks, memory stores, typed commands/state, and async checkpointer ownership

### Requirement: GitNexus setup

The guide SHALL document current index discovery, freshness, and refresh commands without making index mutation an agent capability.

#### Scenario: Index preparation

- **WHEN** an administrator adds a repository
- **THEN** the guide SHALL show how to inspect the GitNexus registry/context and refresh the index from that repository
- **AND** runtime agents SHALL receive query/context/impact authority, not analyze/delete authority

### Requirement: Graphify setup

The guide SHALL document graph discovery and refresh using supported Graphify commands.

#### Scenario: Graph preparation

- **WHEN** an administrator prepares a repository
- **THEN** the guide SHALL use `graphify update .` (and `--force` only when appropriate)
- **AND** it SHALL verify the configured `.graphify/graph.json`

### Requirement: Persistence setup

The guide SHALL distinguish workflow, agent-step, semantic-memory, and artifact persistence.

#### Scenario: Durable workflow

- **WHEN** Postgres durability is configured
- **THEN** the guide SHALL document the async checkpointer DSN source, setup, thread/run ID semantics, restart test, backup, and failure behavior

#### Scenario: No Postgres

- **WHEN** durable workflow persistence is unavailable
- **THEN** the guide SHALL describe non-durable mode accurately
- **AND** it SHALL not claim restart recovery

### Requirement: Gateway and client factories

The guide SHALL use shared TDT factories and centralized credentials.

#### Scenario: Jira and LLM access

- **WHEN** ticket or model access is configured
- **THEN** Jira SHALL use `tdt_core.clients` factories and models SHALL use the agent-core gateway/composition API
- **AND** raw authenticated SDK clients SHALL not be introduced

### Requirement: Authority and artifact operations

The guide SHALL state that the initial release is read-only outside its artifact root.

#### Scenario: Requested mutation

- **WHEN** an operator wants source edits, OpenSpec promotion, Jira updates, GitLab operations, or deployment
- **THEN** the guide SHALL require a separate OpenSpec change and explicit authority review

### Requirement: Observability setup

The guide SHALL configure official instrumentation and TDT correlation/audit policy.

#### Scenario: Telemetry verification

- **WHEN** a test workflow runs
- **THEN** the operator SHALL be able to correlate one workflow/stage span with agent model/tool spans and structured audit events
- **AND** duplicate lifecycle events and secret attributes SHALL fail verification
