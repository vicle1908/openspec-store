## ADDED Requirements

### Requirement: Explicit harness agent composition

`agent-harness` SHALL construct stage agents through the typed `agent_core.sdk` composition API with an explicit gateway, runtime profile, official toolsets/capabilities, and run-scoped instructions.

#### Scenario: Stage agent construction

- **WHEN** a harness stage agent is created
- **THEN** a valid gateway SHALL be supplied before the agent can run
- **AND** the stage SHALL not create a second tool registry or encode capabilities as strings

#### Scenario: Missing gateway

- **WHEN** no gateway can be resolved through the TDT factory
- **THEN** construction SHALL fail before workflow execution with an actionable configuration error

### Requirement: Consumer-owned native graph

`agent-harness` SHALL own a statically declared typed LangGraph state and native graph topology. It SHALL not require an `agent-core` workflow DSL or generate a new `TypedDict` class at runtime.

#### Scenario: Stage modularization

- **WHEN** a stage is extracted into a module
- **THEN** it SHALL expose a native node callable, typed inputs/outputs, validators, and official composition inputs
- **AND** the workflow graph SHALL wire it through native LangGraph node and edge APIs

#### Scenario: Parallel branch

- **WHEN** stages are proven independent by declared read/write sets and reducers
- **THEN** the consumer-owned graph MAY use native fan-out/fan-in
- **AND** parallelism SHALL be determined by topology rather than a stage boolean

### Requirement: Gate routing correctness

Each approval gate SHALL be a dedicated post-stage node that preserves the target stage, artifact digest, run identity, thread identity, and native interrupt identity without a shared fan-out node that can route to unrelated stages.

#### Scenario: Approve one stage

- **WHEN** a decision approves the design gate
- **THEN** only the design continuation SHALL execute
- **AND** other gated stages SHALL remain unreachable until their own predecessors complete

#### Scenario: Resume re-executes gate only

- **WHEN** a gate is resumed
- **THEN** LangGraph MAY re-execute the dedicated gate node
- **AND** the completed artifact-producing stage SHALL not re-execute

#### Scenario: Reject with backtrack

- **WHEN** an authorized rejection includes a valid backtrack target
- **THEN** native `Command(goto=...)` SHALL route only to that target
- **AND** the decision SHALL be recorded once

### Requirement: Unified checkpoint lifecycle

Harness run, stream, status, and resume operations SHALL use the shared `agent-core` LangGraph checkpointer boundary, the same backend and thread identity, the public provisioning contract, and an operation-scoped saver lifetime.

#### Scenario: Durable first run

- **WHEN** durable Postgres checkpointing is enabled
- **THEN** the checkpointer SHALL be initialized through its public setup contract before graph execution

#### Scenario: Durable resume

- **WHEN** a gated durable run is resumed after process restart
- **THEN** resume SHALL compile with the same checkpointer backend and thread ID
- **AND** it SHALL recover the pending native interrupt ID rather than start an in-memory graph
- **AND** it SHALL resume by mapping that interrupt ID to the authorized decision

#### Scenario: Streaming

- **WHEN** a durable run is streamed
- **THEN** streaming SHALL use the same checkpoint policy as non-streaming execution

#### Scenario: Status

- **WHEN** durable workflow status or history is requested
- **THEN** the runner SHALL use public compiled-graph state inspection with the same thread configuration
