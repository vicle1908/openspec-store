## Purpose

Defines the consumer-owned agent-harness composition and durable workflow boundary.

## Requirements

### Requirement: Explicit harness agent composition

`agent-harness` SHALL construct stage agents through the typed `agent_core.sdk` composition API with an explicit model, runtime profile, official toolsets/capabilities, and run-scoped instructions.

#### Scenario: Stage agent construction

- **WHEN** a harness stage agent is created
- **THEN** a valid model SHALL be supplied before the agent can run
- **AND** the stage SHALL not create a second tool registry or encode capabilities as strings

#### Scenario: Missing model

- **WHEN** no model can be resolved through the TDT factory
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

### Requirement: Production graph service wiring

The consumer-owned production graph SHALL invoke stage nodes built from configured production services and official agent/toolset composition. Test-only factories and direct placeholder handlers SHALL NOT be the production execution authority.

#### Scenario: Evidence stage executes

- **WHEN** an evidence-dependent stage runs through the public CLI
- **THEN** its node SHALL receive the immutable stage-service view authorized for that stage
- **AND** the resulting artifact SHALL reference actual inputs, provider evidence, validation result, and source identity

#### Scenario: Deterministic stage executes

- **WHEN** a stage is explicitly classified as a pure deterministic transformation
- **THEN** the graph MAY invoke its pure handler through the same stage-node contract
- **AND** it SHALL still persist an artifact envelope, input references, and validation result

#### Scenario: Stage agent is required

- **WHEN** a stage contract requires model reasoning or official toolsets
- **THEN** the production graph SHALL construct a stage agent with the resolved model, immutable profile, bounded instructions, and stage-visible tools
- **AND** it SHALL not substitute a test factory or uncomposed handler

#### Scenario: Public CLI production fixture

- **WHEN** a production-composition fixture runs from the public CLI boundary
- **THEN** it SHALL produce non-empty requirements and required code-intelligence evidence, persist artifact revisions, and exercise evidence-based review
- **AND** the fixture SHALL fail if production wiring is replaced by empty providers, hard-coded review, or test-only composition

### Requirement: Outcome-quality production fixture

Harness production-path verification SHALL include a bounded fixture that checks meaningful requirements, evidence identity, artifact persistence, and review outcomes rather than only graph completion.

#### Scenario: Fixture proves outcome quality

- **WHEN** the public CLI runs the production fixture
- **THEN** it SHALL produce non-empty required artifacts with accepted evidence references and truthful validation outcomes
- **AND** the evaluation SHALL record execution and quality results separately

#### Scenario: Fixture exposes placeholder wiring

- **WHEN** providers are empty, review is hard-coded, or a test-only composition path is selected
- **THEN** the fixture SHALL fail deterministically
- **AND** the result SHALL identify the missing production boundary

### Requirement: Replay-safe production persistence

Production run, resume, and report SHALL use a persistent checkpointer and stable run/thread identity. In-memory checkpointers SHALL be rejected for production fixtures, and graph state SHALL be bounded JSON-safe references with live dependencies reconstructed per process.

#### Scenario: Interrupted node resumes

- **WHEN** framework interrupt semantics restart a node from its beginning
- **THEN** artifact writes and external effects SHALL be idempotent under the stable run, node, attempt, and operation identity
- **AND** non-idempotent I/O SHALL NOT occur before an interrupt unless it is wrapped in a durable replay-aware operation

#### Scenario: Paused run crosses a deployment

- **WHEN** node names, state fields, artifact/reference schemas, or toolset definitions differ from the paused-run version
- **THEN** compatibility handling SHALL migrate an explicitly supported version or reject it before continuation
- **AND** unknown versions SHALL not be reinterpreted silently

#### Scenario: Durable tool approval resumes

- **WHEN** an agent-backed stage resumes a deferred tool call
- **THEN** the durable agent and toolset SHALL have stable IDs and the decision SHALL bind the exact original tool-call ID and normalized arguments
- **AND** the resolved per-stage tool list, approval policy, and reconstructed dependency container SHALL be verified before execution

### Requirement: Authenticated gate decisions

Harness approval and rejection decisions SHALL bind a trusted authenticated subject and unique single-use nonce to the exact gate interrupt, artifact digest, run, repository, expiry, and policy version, and SHALL revalidate subject freshness, revocation, assurance, and policy generation at final resume. The default resolver SHALL fail-closed when no ratified adapter is configured. Caller-supplied identity text SHALL NOT serve as an authorization source.

#### Scenario: Authenticated gate approval

- **WHEN** a valid subject approves a pending gate after process restart
- **THEN** only the bound continuation SHALL execute
- **AND** the audit record SHALL identify the resolved subject and authentication provenance without credential values

#### Scenario: Spoofed or replayed decision

- **WHEN** a caller self-asserts identity or replays a decision for a different or terminal gate
- **THEN** the decision SHALL fail before graph continuation
- **AND** no successful gate event SHALL be recorded

#### Scenario: Default resolver denies authorization

- **GIVEN** no explicit resolver is provided to the workflow runner
- **WHEN** a gate resume is attempted
- **THEN** the authorization SHALL fail with `GateIdentityUnavailableError`
- **AND** any environment identity (e.g. `TDT_ACTOR_ID`) SHALL NOT be used for authorization

#### Scenario: Caller-supplied actor is display-only

- **GIVEN** an explicit resolver that returns a valid subject
- **WHEN** a gate resume includes `actor` text
- **THEN** the trusted decision SHALL use the resolver-returned subject ID
- **AND** the caller-supplied actor text SHALL appear only in display fields

#### Scenario: Separation of duties enforced

- **GIVEN** a valid authenticated subject that matches the gate initiator
- **WHEN** authorization is attempted
- **THEN** the authorization SHALL fail with `separation_of_duties_required`

#### Scenario: Expired gate fails before resolver call

- **GIVEN** a gate binding whose expiry is in the past
- **WHEN** authorization is attempted
- **THEN** the authorization SHALL fail with `gate_decision_expired`
- **AND** the resolver SHALL NOT be called
