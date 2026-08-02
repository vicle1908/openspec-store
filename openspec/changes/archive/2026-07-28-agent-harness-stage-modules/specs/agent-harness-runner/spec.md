## ADDED Requirements

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

The runner SHALL consume harness domain configuration containing an immutable core runtime profile.

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
