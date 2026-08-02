# Architecture Decisions

## Purpose

Define how architectural decisions are recorded, stored, and surfaced within the agent harness workflow.

## Requirements

### Requirement: Decision record format

Every architectural decision SHALL be recorded with a unique identifier, title, status, context, decision statement, rationale, alternatives considered, and consequences.

#### Scenario: Record creation

- **WHEN** an architectural decision is made
- **THEN** the system SHALL create a decision record with all required fields

#### Scenario: Record fields

- **WHEN** a decision record is read
- **THEN** it SHALL contain id, title, status, context, decision, rationale, alternatives, and consequences

### Requirement: Decision lifecycle

Decisions SHALL progress through proposed, accepted, deprecated, and superseded statuses. Status transitions SHALL be logged.

#### Scenario: Status transition

- **WHEN** a decision status changes
- **THEN** the transition SHALL be logged with timestamp and actor

#### Scenario: Supersession

- **WHEN** a new decision supersedes an existing one
- **THEN** the old decision SHALL reference the new one and its status SHALL change to superseded

### Requirement: Decision traceability

Decisions SHALL be linked to the artifacts they influence and the requirements they address.

#### Scenario: Decision links

- **WHEN** a decision influences an artifact
- **THEN** the decision record SHALL reference the artifact
- **AND** the artifact SHALL reference the decision

### Requirement: Decision querying

The system SHALL support querying decisions by status, artifact reference, and keyword.

#### Scenario: Query by status

- **WHEN** a user queries decisions by status
- **THEN** the system SHALL return all decisions matching the status

#### Scenario: Query by artifact

- **WHEN** a user queries decisions linked to an artifact
- **THEN** the system SHALL return all decisions referencing that artifact
