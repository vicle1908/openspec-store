## ADDED Requirements

### Requirement: Native workflow-stage interrupts

Configured stage gates SHALL pause through native LangGraph `interrupt` and resume through `Command(resume=...)`.

#### Scenario: Gate requests a decision

- **WHEN** a required gate is reached
- **THEN** the node SHALL interrupt with a typed request containing decision ID, workflow run ID, ticket ID, stage, artifact digest/summary, allowed decisions, approvers, expiry, and backtrack targets
- **AND** the checkpointer SHALL persist the pending interrupt

#### Scenario: Approved gate resumes

- **WHEN** an authorized actor approves a current pending decision
- **THEN** the CLI SHALL resume the same `thread_id` with a typed decision
- **AND** the workflow SHALL continue without replaying completed stages

#### Scenario: Rejected gate backtracks

- **WHEN** an authorized actor rejects with a permitted backtrack target and reason
- **THEN** the resumed node SHALL return a native `Command` updating the decision trace and routing to that target

### Requirement: Stage-gate authorization

The consumer SHALL authenticate and authorize every stage-gate decision before graph resume.

#### Scenario: Valid local actor

- **WHEN** the authenticated operating-system/session identity is listed for the gate
- **THEN** its current, unexpired decision SHALL be accepted
- **AND** the identity and decision ID SHALL be audited

#### Scenario: Unauthorized or stale decision

- **WHEN** the actor is not authorized, the decision ID is unknown/resolved, the stage differs, or the decision has expired
- **THEN** resume SHALL be rejected
- **AND** the workflow SHALL remain paused

### Requirement: Deterministic gate policy

Gate requirement, timeout, escalation, and auto-approval SHALL be host-evaluated policy.

#### Scenario: Deterministic auto-approval

- **WHEN** a configured typed condition evaluates true from validated state
- **THEN** the host MAY record an automatic approval
- **AND** the condition and evaluated inputs SHALL be audited

#### Scenario: Model-authored authorization

- **WHEN** a model suggests that its own artifact should be approved
- **THEN** that suggestion SHALL have no authorization effect

#### Scenario: Timeout

- **WHEN** a gate expires without a decision
- **THEN** it SHALL enter the configured reject-or-escalate state
- **AND** it SHALL never silently approve

### Requirement: Tool approval remains native and separate

Approval of an individual Pydantic AI tool call SHALL use native deferred tool requests/results and SHALL not be conflated with a workflow-stage interrupt.

#### Scenario: Tool requires authorization

- **WHEN** an agent requests an approval-required tool
- **THEN** its upstream tool-call ID SHALL be preserved through `DeferredToolRequests` and `DeferredToolResults`
- **AND** the stage gate decision SHALL not authorize unrelated tool calls

### Requirement: Initial approval transport

The first release SHALL support the authenticated local CLI as the only approval transport.

#### Scenario: Unsupported transport

- **WHEN** webhook, Jira comment, chat, or email approval is requested
- **THEN** configuration SHALL reject it as unsupported
- **AND** a separate OpenSpec change SHALL be required before enabling it

### Requirement: Gate observability

Gate lifecycle events SHALL be emitted once through the supported audit/instrumentation path.

#### Scenario: Gate lifecycle

- **WHEN** a gate is requested, approved, rejected, expired, escalated, or resumed
- **THEN** one structured event SHALL include workflow run ID, decision ID, stage, actor when applicable, and correlation ID
- **AND** artifact content or secrets SHALL not be embedded in the event
