# Anti-Hallucination

## Purpose

Define requirements for preventing hallucinated evidence, fabricated artifacts, and fictional tool outputs in the agent harness workflow.

## Requirements

### Requirement: Evidence origin attestation

Every evidence record SHALL carry an origin field identifying which tool or source produced it. The system SHALL reject evidence with missing or unrecognized origin values.

#### Scenario: Valid evidence

- **WHEN** a tool produces evidence
- **THEN** the evidence record SHALL include an origin field matching a registered tool or source identifier
- **AND** the runtime SHALL accept the evidence for downstream use

#### Scenario: Missing origin

- **WHEN** an evidence record lacks an origin field
- **THEN** the runtime SHALL reject the evidence and report the validation failure

#### Scenario: Unrecognized origin

- **WHEN** an evidence record contains an origin not registered in the tool registry
- **THEN** the runtime SHALL reject the evidence and list available registered origins

### Requirement: Tool output verification

All tool outputs consumed as evidence SHALL be verified against the tool declared output schema before acceptance into the evidence registry.

#### Scenario: Schema match

- **WHEN** a tool returns output matching its declared schema
- **THEN** the output SHALL be accepted and stored as evidence

#### Scenario: Schema mismatch

- **WHEN** a tool returns output that does not match its declared schema
- **THEN** the output SHALL be rejected with a descriptive validation error

### Requirement: Fabrication detection heuristics

The system SHALL apply heuristic checks to detect likely fabricated content, including references to non-existent files, functions, or commits.

#### Scenario: Non-existent file reference

- **WHEN** evidence references a file path that does not exist on disk
- **THEN** the system SHALL flag the evidence as suspect and require manual verification

#### Scenario: Non-existent symbol reference

- **WHEN** evidence references a function or class name that cannot be resolved via code intelligence
- **THEN** the system SHALL flag the evidence as suspect

### Requirement: Audit trail for evidence acceptance

Every evidence acceptance or rejection event SHALL be logged in the append-only trace with actor identity and reason.

#### Scenario: Acceptance logged

- **WHEN** evidence is accepted into the registry
- **THEN** the trace SHALL record the acceptance event with origin, validator identity, and timestamp

#### Scenario: Rejection logged

- **WHEN** evidence is rejected
- **THEN** the trace SHALL record the rejection event with origin, failure reason, and timestamp
