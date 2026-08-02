# Data Model

## Purpose

Define core data structures for the agent harness: artifact, stage, gate decision, run, trace, validation, runtime, and workspace representations. Establishes how artifacts, workflows, and configuration are serialized and referenced across the system.

## Requirements

### Requirement: Artifact data model

Artifacts SHALL be represented with identity, kind, stage ownership, schema version, content reference, content digest, status, created timestamp, and revision counter.

#### Scenario: Artifact representation

- **WHEN** an artifact is created or revised
- **THEN** it SHALL carry identity, kind, stage owner, schema version, content reference, content digest, status, created timestamp, and revision counter

#### Scenario: Artifact kind

- **WHEN** an artifact is classified
- **THEN** its kind SHALL be one of: `design`, `spec`, `task-list`, `test-plan`, `verification-report`, or another harness-defined kind

### Requirement: Stage data model

Stages SHALL be represented with identity, kind, status, inputs, outputs, evidence references, dependencies, and failure information.

#### Scenario: Stage representation

- **WHEN** a stage is executed
- **THEN** it SHALL carry identity, kind, status, inputs, outputs, evidence references, dependencies, and failure information when applicable

#### Scenario: Stage kind

- **WHEN** a stage is classified
- **THEN** its kind SHALL be one of the standard harness stages or a custom defined stage

### Requirement: Gate decision data model

Gate decisions SHALL be represented with identity, checkpoint reference, decision kind, actor identity, optional reason, optional backtrack target, timestamp, and resume instruction.

#### Scenario: Gate decision representation

- **WHEN** a gate decision is recorded
- **THEN** it SHALL carry identity, checkpoint reference, decision kind, actor identity, reason when present, backtrack target when present, timestamp, and resume instruction

### Requirement: Run data model

Workflow runs SHALL be represented with identity, ticket reference, status, start time, end time, current stage, stage history, and configuration snapshot.

#### Scenario: Run representation

- **WHEN** a workflow run is initiated
- **THEN** it SHALL carry identity, ticket reference, status, start time, current stage, stage history, and configuration snapshot

### Requirement: Trace data model

Trace entries SHALL be append-only within a run. Each entry SHALL carry workflow run ID, ticket ID, stage, revision, artifact reference, digest, input references, evidence references, validation results, gate decision ID, timestamp, and duration.

#### Scenario: Trace entry

- **WHEN** a trace entry is recorded
- **THEN** it SHALL carry the complete trace entry fields and remain immutable once written

### Requirement: Validation data model

Validation results SHALL be represented with validator identity, status, severity, message, and affected artifacts.

#### Scenario: Validation result

- **WHEN** validation runs
- **THEN** each result SHALL carry validator identity, pass/fail status, severity, message, and affected artifact references

### Requirement: Runtime state representation

Runtime state SHALL include workflow mode, resume state, evidence registry reference, memory reference, durability configuration, and observability configuration.

#### Scenario: Runtime state

- **WHEN** a workflow is active
- **THEN** runtime state SHALL carry all operational state needed to resume and observe the workflow

### Requirement: Workspace representation

Workspace configuration SHALL include project identity, repo map, shared directory, configuration sources, and environment variable set.

#### Scenario: Workspace config

- **WHEN** a workspace is configured
- **THEN** it SHALL provide project identity, repo map, shared directory, configuration sources, and environment variables
