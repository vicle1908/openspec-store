# Agent Harness Runner Specification

## Purpose

Define unified run, stream, inspection, and durable-resume behavior for the planning harness.
## Requirements
### Requirement: Unified runner execution contract

Run, stream, status inspection, and resume SHALL use the same consumer-owned graph, shared `agent-core` checkpointer boundary, configured backend, and thread identity.

#### Scenario: Non-durable run

- **WHEN** persistence is disabled
- **THEN** run and stream SHALL use the documented non-durable execution policy
- **AND** resume after process restart SHALL report that no durable checkpoint exists

#### Scenario: Durable run

- **WHEN** Postgres persistence is enabled
- **THEN** first-use provisioning SHALL complete through the shared boundary before compile
- **AND** the resource SHALL remain open for the operation lifetime

### Requirement: Durable interrupt resume

A durable gated workflow SHALL resume after process restart through the same saver backend and `thread_id`.

#### Scenario: Resume after restart

- **WHEN** a valid decision is submitted for a persisted pending interrupt
- **THEN** the runner SHALL read the pending native interrupt ID from public graph state
- **AND** it SHALL invoke `Command(resume={pending_interrupt.id: decision})` on the recovered thread
- **AND** completed stages SHALL not rerun

#### Scenario: Unknown run

- **WHEN** no checkpoint exists for the run ID
- **THEN** resume SHALL fail without starting a new run

### Requirement: Trusted durable checkpoint deserialization

Every durable harness lifecycle operation SHALL configure the shared
`agent-core` checkpointer with an explicit allowlist containing only the
trusted custom types reachable from the harness checkpoint state. The lifecycle
SHALL remain functional when LangGraph strict MessagePack enforcement is
enabled and SHALL NOT enable unrestricted module deserialization.

#### Scenario: Separate process reads a strict checkpoint

- **WHEN** one CLI process persists a gated run and a separate `status`, `report`, `approve`, or `reject` process opens the same PostgreSQL checkpoint with `LANGGRAPH_STRICT_MSGPACK=true`
- **THEN** every registered harness artifact, enum, gate, trace, and evidence value SHALL deserialize successfully
- **AND** checkpointed artifact models and their nested enums SHALL retain their declared runtime types rather than degrading to raw mappings or scalars
- **AND** standard error SHALL contain no unregistered MessagePack type warning
- **AND** JSON mode SHALL continue to emit exactly one valid JSON document on standard output

#### Scenario: Checkpoint contains an untrusted custom type

- **WHEN** strict MessagePack deserialization encounters a custom type that is not in the explicit harness allowlist
- **THEN** the lifecycle operation SHALL NOT treat degraded raw artifact data as proof of typed checkpoint compatibility
- **AND** it SHALL NOT broaden the allowlist to a module wildcard or unrestricted mode

#### Scenario: Existing durable checkpoint remains compatible

- **WHEN** a checkpoint written before explicit allowlist configuration contains only types covered by the trusted harness state contract
- **THEN** a strict lifecycle process SHALL read and resume that checkpoint without rewriting completed stages

### Requirement: Streaming parity

Streaming SHALL have the same checkpoint, authority, validation, budget, and error semantics as non-streaming execution.

#### Scenario: Stream durable workflow

- **WHEN** durable streaming pauses at a gate
- **THEN** status and resume SHALL observe the same pending interrupt

### Requirement: Public workflow status inspection

The runner SHALL read durable workflow status and history through public compiled-graph state APIs.

#### Scenario: Read current status

- **WHEN** status is requested for a known durable thread
- **THEN** the runner SHALL use `aget_state` with that thread configuration
- **AND** it SHALL report pending nodes and native interrupts without querying saver internals

#### Scenario: Read history

- **WHEN** audit history is requested
- **THEN** the runner SHALL use bounded `aget_state_history`

### Requirement: Composed runner configuration

The runner SHALL compose an immutable canonical resolved agent profile with source-preserved harness domain configuration. Model and runtime LLM fields SHALL use the canonical precedence contract. Harness-owned gate, persistence, authority, validation, budget, and retention sections SHALL come only from the selected harness overlay and declared environment keys, never from same-named global sections. The legacy default harness config path SHALL not be read automatically, and explicit config files SHALL use the canonical top-level schema.

#### Scenario: Stage override

- **WHEN** a stage needs different limits or model settings
- **THEN** it SHALL receive an immutable run-scoped copy
- **AND** the parent profile SHALL remain unchanged

#### Scenario: Canonical durable environment

- **WHEN** durable settings are supplied through the canonical environment boundary
- **THEN** registered harness environment keys SHALL populate the declared persistence fields
- **AND** the harness SHALL NOT create a second dotenv loader or accept undeclared aliases

#### Scenario: Harness config resolves from agent-specific YAML

- **GIVEN** the agent-specific harness YAML contains model and runtime values
- **WHEN** runner configuration is loaded
- **THEN** its runtime profile SHALL use the canonically resolved values
- **AND** its model and settings projections SHALL agree

#### Scenario: HARNESS environment variables override agent-specific YAML

- **GIVEN** a registered harness environment value conflicts with agent YAML
- **WHEN** runner configuration is loaded
- **THEN** the environment value SHALL win
- **AND** provenance SHALL identify the registered key name

#### Scenario: Domain sections are source-preserved

- **GIVEN** the harness overlay contains gate, persistence, or authority settings
- **WHEN** runner configuration is loaded
- **THEN** those settings SHALL be read from that overlay
- **AND** same-named global sections SHALL not contribute

#### Scenario: Legacy config path is ignored

- **GIVEN** only the removed legacy harness config path exists
- **WHEN** runner configuration is loaded without an explicit path
- **THEN** it SHALL use agent/global/default sources permitted by the canonical contract
- **AND** it SHALL not read the legacy file

#### Scenario: Explicit legacy wrapper is rejected

- **GIVEN** an explicitly selected config file contains the legacy harness wrapper
- **WHEN** runner configuration is loaded
- **THEN** it SHALL fail with migration guidance to canonical top-level sections

#### Scenario: Explicit config path has canonical parity

- **GIVEN** a caller supplies an explicit `config_path` containing canonical top-level sections
- **WHEN** runner configuration is loaded
- **THEN** it SHALL apply the same precedence, overlay-key policy, path containment, and source-provenance rules as the standard agent path
- **AND** it SHALL not use the removed legacy wrapper or a second YAML loader

#### Scenario: Domain sections sourced from agent overlay only

- **GIVEN** `~/.tdt/agents/agent-harness.yaml` contains `gate: {approvers: ["alice"]}`
- **AND** `~/.tdt/config.yaml` does NOT contain a `gate` key
- **WHEN** `HarnessConfig.load()` is called
- **THEN** `config.gate.approvers` SHALL be `["alice"]`
- **AND** the value SHALL have been read by `load_agent_overlay("agent-harness")`

#### Scenario: Global config does not supply domain sections

- **GIVEN** `~/.tdt/config.yaml` contains `gate: {approvers: ["bob"]}`
- **AND** `~/.tdt/agents/agent-harness.yaml` does NOT contain a `gate` key
- **WHEN** `HarnessConfig.load()` is called
- **THEN** `config.gate.approvers` SHALL use the `HarnessConfig` field default (empty list)
- **AND** the value `"bob"` SHALL NOT appear in the configuration

#### Scenario: Explicit config_path overrides agent overlay path

- **GIVEN** an explicit `config_path` is provided to `HarnessConfig.load()`
- **WHEN** `HarnessConfig.load(config_path=path)` is called
- **THEN** both `load_agent_config()` and `load_agent_overlay()` SHALL use the explicit path as the agent overlay source
- **AND** the standard `~/.tdt/agents/agent-harness.yaml` SHALL NOT be read

#### Scenario: Legacy harness wrapper rejected

- **GIVEN** an explicit config file contains a `harness:` top-level wrapper section
- **WHEN** `HarnessConfig.load(config_path=path)` is called
- **THEN** a `ConfigMigrationError` SHALL be raised directing the operator to use top-level sections

#### Scenario: Missing agent-specific config falls back to global defaults

- **GIVEN** no agent-specific harness overlay exists
- **WHEN** runner configuration is loaded
- **THEN** global LLM values and typed domain defaults SHALL be used
- **AND** registered environment values SHALL still apply

#### Scenario: Production services propagate the effective model

- **WHEN** production services are constructed from a valid runner configuration
- **THEN** `production_services().model` SHALL equal `config.model`
- **AND** every agent-backed stage SHALL receive the effective model and model behavior from that configuration
- **AND** stage construction SHALL not observe a missing model caused by composition loss

#### Scenario: Domain overlay does not alter the LLM profile

- **GIVEN** an agent overlay contains harness gate, persistence, authority, validation, budget, or retention sections
- **WHEN** runner configuration is composed
- **THEN** those sections SHALL remain source-preserved harness domain data
- **AND** they SHALL not override same-named global LLM or provider fields

#### Scenario: Unsafe or unresolved artifact root

- **WHEN** the configured artifact root is relative, remains an unexpanded variable, escapes the approved root, or traverses a disallowed link
- **THEN** production-service construction SHALL fail before creating a directory or writing an artifact

#### Scenario: Default artifact root with TDT_HOME unset

- **GIVEN** `TDT_HOME` is unset
- **WHEN** the default artifact root is resolved
- **THEN** it SHALL resolve beneath the canonical default TDT root
- **AND** no literal `$TDT_HOME` path component SHALL be created

### Requirement: Protected CLI lifecycle preflight

The `agent-harness` CLI SHALL validate gate authorization and persistence
before starting a run that contains protected interrupt stages. A protected
CLI run SHALL require a non-empty approver allowlist, durable persistence, and
a configured PostgreSQL URL. The programmatic `WorkflowRunner` API MAY retain
explicit same-process, non-durable behavior.

#### Scenario: Missing approver policy

- **WHEN** a CLI run enables protected interrupt stages with no approvers
- **THEN** the command SHALL exit non-zero before executing the intake stage
- **AND** the error SHALL identify the supported approver configuration

#### Scenario: Missing durable persistence

- **WHEN** a CLI run enables protected interrupt stages without durable
  persistence and a PostgreSQL URL
- **THEN** the command SHALL exit non-zero before executing the intake stage
- **AND** the error SHALL explain that cross-process status and decisions
  require `HARNESS_DURABLE=true` and `TDT_POSTGRES_URL`

#### Scenario: Lifecycle command lacks durable configuration

- **WHEN** `status`, `report`, `approve`, or `reject` is invoked without a
  durable PostgreSQL configuration
- **THEN** the command SHALL fail before graph compilation or checkpoint access
- **AND** it SHALL NOT construct an in-memory saver as an implicit fallback

#### Scenario: Explicit programmatic non-durable run

- **WHEN** an application creates one `WorkflowRunner` instance with
  non-durable persistence and resumes it within the same process
- **THEN** the existing in-process checkpoint policy SHALL remain available
- **AND** it SHALL NOT be represented as restart-safe

### Requirement: Configuration-consistent CLI commands

The `run`, `status`, `report`, `approve`, and `reject` commands SHALL resolve
the same harness configuration contract, checkpoint backend, and thread ID.
Every lifecycle command SHALL support the canonical `$TDT_HOME` configuration
and the same explicit configuration-file override.

#### Scenario: Resume after CLI process restart

- **WHEN** a protected durable run pauses at a gate and the original CLI
  process exits
- **THEN** a later `status`, `approve`, or `reject` process using the same
  configuration SHALL recover the checkpoint and pending native interrupt
- **AND** completed artifact-producing stages SHALL not rerun

#### Scenario: Configuration override parity

- **WHEN** `run --config <path>` creates a durable run
- **THEN** `status`, `report`, `approve`, and `reject` SHALL accept the same
  `--config <path>` override
- **AND** no command SHALL silently fall back to an in-memory backend

#### Scenario: Run absent from configured backend

- **WHEN** a lifecycle command cannot find the requested run in its configured
  checkpoint backend
- **THEN** it SHALL fail without creating a new run or checkpoint
- **AND** it SHALL return the stable `run_not_found` code naming the run and
  configured backend class without disclosing the database URL or credentials

### Requirement: Stable CLI error contract

Expected configuration, persistence, authorization, and unknown-run failures
SHALL be returned as concise user-facing errors without a Rich Python
traceback. JSON mode SHALL emit exactly one valid JSON error document on
standard output and return a non-zero exit code.

#### Scenario: Human-readable configuration failure

- **WHEN** a required gate or persistence setting is missing in text mode
- **THEN** the command SHALL print the setting name, remediation, and non-zero
  exit status without an implementation traceback

#### Scenario: JSON unknown-run failure

- **WHEN** `status --json` requests an unknown run
- **THEN** standard output SHALL contain one JSON object with stable `code`,
  `message`, and `run_id` fields
- **AND** diagnostic logging SHALL not corrupt that JSON document

