## MODIFIED Requirements

### Requirement: One-target gate interrupts

Each human approval gate SHALL be a dedicated post-stage node that interrupts for exactly one continuation. Request identity, issued-at time, and expiry SHALL be derived from checkpointed run, thread, stage, artifact identity/digest, the artifact's timezone-aware UTC creation time, and configured TTL. Allowed routing and an explicit approver allowlist SHALL be preserved with the request. Native interrupt identity SHALL be bound through public graph state and SHALL NOT be regenerated or inferred during resume. The acting principal and decision audit time SHALL be supplied by the trusted runner boundary rather than accepted from user decision data.

#### Scenario: Gate re-execution

- **WHEN** LangGraph re-executes a dedicated gate node for the same pending request
- **THEN** the gate SHALL deterministically reproduce the same request identity, issued-at time, expiry time, artifact digest, allowed routing, and approver set from checkpointed inputs
- **AND** re-execution SHALL NOT extend expiry or create a second logical decision

#### Scenario: Approval

- **WHEN** the trusted boundary resolves an authorized actor and receives an unexpired decision matching the request, run, thread, stage, artifact digest, and pending native interrupt
- **THEN** native `Command(resume={pending_interrupt.id: decision})` SHALL deliver the decision to the matching gate
- **AND** the dedicated gate MAY re-execute as required by LangGraph
- **AND** artifact generation and validation SHALL not re-execute
- **AND** only that gate's continuation SHALL run

#### Scenario: Rejection and backtrack

- **WHEN** an authorized rejection names an allowed backtrack target
- **THEN** native `Command(goto=...)` SHALL route only to the validated target
- **AND** the decision SHALL be recorded exactly once

#### Scenario: Invalid decision

- **WHEN** a decision is expired according to the runner's trusted UTC clock, replayed, submitted by an unauthorized resolved actor, contains a self-asserted actor or authorization timestamp, belongs to another request/run/thread/stage/artifact/interrupt, or targets forbidden routing
- **THEN** the workflow SHALL fail closed before advancing or modifying the checkpoint
- **AND** the rejection SHALL be observable without recording the invalid decision as approved workflow history

#### Scenario: Missing approver policy

- **WHEN** protected interrupt stages are configured without a non-empty approver allowlist
- **THEN** graph construction SHALL fail with actionable configuration guidance
- **AND** the workflow SHALL NOT begin execution

#### Scenario: Non-durable gated run

- **WHEN** a gated workflow runs without durable Postgres persistence
- **THEN** it SHALL use an in-process checkpointer retained for the runner lifetime
- **AND** same-process resume MAY be supported
- **AND** resume after process restart SHALL report that no durable checkpoint exists
