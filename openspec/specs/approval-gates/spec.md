# Approval Gates

## Purpose

Define human approval gate requirements for the agent harness workflow, including checkpoint definitions, approval/rejection mechanics, backtracking, authentication, audit trails, and enforcement.

## Requirements

### Requirement: Required approval checkpoints

Approval gates SHALL be enforced before design approval, implementation start, and verification completion. Each checkpoint SHALL define required evidence and approver roles.

#### Scenario: Design checkpoint

- **WHEN** design stage completes
- **THEN** the system SHALL block progress until an authorized approver reviews the design artifact
- **AND** the approver SHALL have visibility into design completeness and evidence

#### Scenario: Implementation checkpoint

- **WHEN** implementation plan is ready
- **THEN** the system SHALL require approval before coding begins

#### Scenario: Verification checkpoint

- **WHEN** verification stage completes
- **THEN** the system SHALL require approval before workflow completion

### Requirement: Approval and rejection mechanics

The system SHALL support approve, reject with reason, and reject with backtrack actions at each gate.

#### Scenario: Approve

- **WHEN** an authorized actor approves a gate
- **THEN** the system SHALL record the decision and advance the workflow to the next stage

#### Scenario: Reject

- **WHEN** an authorized actor rejects a gate
- **THEN** the system SHALL record the rejection with a reason and halt or redirect the workflow

#### Scenario: Reject with backtrack

- **WHEN** an authorized actor rejects with a backtrack target
- **THEN** the system SHALL rewind to the specified stage and resume from there

### Requirement: Actor authentication and authorization

All gate decisions SHALL require authenticated actor identity. Actor roles SHALL be validated against checkpoint requirements.

#### Scenario: Authenticated decision

- **WHEN** a gate decision is submitted
- **THEN** actor identity SHALL be derived from authenticated session context
- **AND** the system SHALL verify the actor has the required role for the checkpoint

#### Scenario: Unauthorized attempt

- **WHEN** an actor lacks the required role
- **THEN** the system SHALL reject the decision with an authorization error

### Requirement: Gate audit trail

All gate decisions SHALL be logged in the append-only trace with actor identity, decision, timestamp, and rationale.

#### Scenario: Decision logged

- **WHEN** a gate decision is recorded
- **THEN** the trace SHALL contain actor, decision kind, rationale, and timestamp

### Requirement: Gate enforcement

Gates SHALL be enforced by default. Bypassing a gate SHALL require explicit configuration and administrative override.

#### Scenario: Default enforcement

- **WHEN** a workflow reaches a gate
- **THEN** the gate SHALL block progress until a valid decision is recorded

#### Scenario: Configured bypass

- **WHEN** a gate is configured for bypass
- **THEN** the bypass SHALL be logged in the trace with the administrative override identity
