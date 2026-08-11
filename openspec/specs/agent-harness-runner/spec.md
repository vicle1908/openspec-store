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

The runner SHALL consume harness domain configuration containing an immutable core runtime profile. Model and runtime settings SHALL be resolved through `load_agent_config("agent-harness")` for the merged LLM configuration. Harness domain sections (`gate`, `persistence`, `authority`, `validation`, `budget`, `retention`) SHALL be resolved through `load_agent_overlay("agent-harness")`, which preserves source provenance by reading the agent YAML file directly without merging with the global config. Domain keys validated by `allowed_overlay_keys` in `load_agent_config()` SHALL be accepted without error but SHALL NOT appear in the merged LLM result — `load_agent_overlay()` is the sole source for harness domain sections. `HARNESS_*` environment variables SHALL retain precedence over agent-specific YAML values. The legacy `$TDT_HOME/harness/config.yaml` path SHALL NOT be read automatically.

#### Scenario: Stage override

- **WHEN** a stage needs different limits or model settings
- **THEN** it SHALL receive an immutable profile copy and run-scoped inputs
- **AND** the parent harness configuration SHALL remain unchanged

#### Scenario: Canonical durable environment

- **WHEN** durable settings are supplied through `$TDT_HOME/.env` or the process environment
- **THEN** `HarnessConfig.load()` SHALL delegate dotenv loading to `tdt_core.env.load_tdt_env()`
- **AND** `HARNESS_DURABLE` SHALL populate `persistence.durable`
- **AND** `TDT_POSTGRES_URL` SHALL populate `persistence.postgres_url`
- **AND** the harness SHALL NOT create a second settings loader or require `HARNESS_PERSISTENCE_DURABLE`

#### Scenario: Harness config resolves from agent-specific YAML

- **GIVEN** `~/.tdt/agents/agent-harness.yaml` exists with model, max_iterations, and timeout_seconds
- **WHEN** `HarnessConfig.load()` is called
- **THEN** configuration SHALL be resolved from `~/.tdt/agents/agent-harness.yaml` via `load_agent_config("agent-harness")`
- **AND** the loaded values SHALL be used for runtime settings

#### Scenario: HARNESS environment variables override agent-specific YAML

- **GIVEN** `~/.tdt/agents/agent-harness.yaml` specifies `durable: false`
- **AND** `HARNESS_DURABLE=true` is set in the environment
- **WHEN** `HarnessConfig.load()` is called
- **THEN** `config.persistence.durable` SHALL be `true`
- **AND** the environment variable SHALL take precedence

#### Scenario: Legacy config path is ignored

- **GIVEN** only `$TDT_HOME/harness/config.yaml` exists (no `~/.tdt/agents/agent-harness.yaml`)
- **WHEN** `HarnessConfig.load()` is called
- **THEN** configuration SHALL fall back to global TDT defaults and code defaults
- **AND** the legacy path SHALL NOT be read

#### Scenario: Missing agent-specific config falls back to global defaults

- **GIVEN** neither `~/.tdt/agents/agent-harness.yaml` nor `$TDT_HOME/harness/config.yaml` exists
- **WHEN** `HarnessConfig.load()` is called
- **THEN** code defaults SHALL be used without error
- **AND** `HARNESS_*` environment variables SHALL still be applied

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

