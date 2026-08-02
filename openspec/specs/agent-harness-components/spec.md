# agent-harness-components Specification

## Purpose
Defines the core components of agent-harness: workflow runner, artifact store, checkpoint system, and gate decisions.
## Requirements
### Requirement: Workflow runner

The workflow runner SHALL execute stages, manage state, and handle interrupts.

#### Scenario: Stage execution

- **WHEN** a stage is executed
- **THEN** the runner SHALL load the current state from checkpoints
- **AND** execute the stage with the appropriate agent
- **AND** persist the artifact to the artifact store
- **AND** save the new state to checkpoints

#### Scenario: Interrupt handling

- **WHEN** a gate requires human approval
- **THEN** the runner SHALL create an interrupt
- **AND** wait for human decision
- **AND** record the decision in the gate decision store

### Requirement: Artifact store

The artifact store SHALL manage versioned artifact envelopes with integrity verification.

#### Scenario: Artifact commit

- **WHEN** an artifact is committed
- **THEN** it SHALL be written as a temporary file
- **AND** flushed to disk
- **AND** atomically renamed
- **AND** the containing directory SHALL be flushed
- **AND** the SHA-256 digest SHALL be verified

#### Scenario: Artifact verification

- **WHEN** an artifact is loaded
- **THEN** its SHA-256 digest SHALL be verified
- **AND** mismatch SHALL reject the artifact

### Requirement: Checkpoint system

The checkpoint system SHALL enable resume from any stage with full state recovery.

#### Scenario: Checkpoint save

- **WHEN** a stage completes
- **THEN** a checkpoint SHALL be saved with run_id, stage, artifact_digest, and state hash
- **AND** the checkpoint SHALL be persisted to PostgreSQL

#### Scenario: Checkpoint load

- **WHEN** a workflow is resumed
- **THEN** the latest checkpoint SHALL be loaded
- **AND** its integrity SHALL be verified
- **AND** the state SHALL be restored

### Requirement: Gate decisions

The gate system SHALL manage human approval points and decisions.

#### Scenario: Gate interrupt

- **WHEN** a gate requires human approval
- **THEN** an interrupt SHALL be created with the gate requirements
- **AND** the interrupt SHALL be sent to the configured approver

#### Scenario: Decision recording

- **WHEN** a gate decision is made
- **THEN** it SHALL be recorded with run_id, stage, decision_id, approver, decision, reason, nonce, and timestamp
- **AND** the decision SHALL be immutable

