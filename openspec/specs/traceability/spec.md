## Purpose

This specification defines requirements for Traceability.

## Requirements

### Requirement: Evidence-backed artifact lineage

Every stage artifact SHALL identify its inputs, evidence, validator results, revisions, and content digest.

#### Scenario: Artifact trace entry

- **WHEN** a stage persists an artifact revision
- **THEN** it SHALL append a typed trace entry containing workflow run ID, ticket ID, stage, revision, artifact reference, digest, input artifact references, evidence references, validation results, gate decision ID when applicable, timestamp, and duration

#### Scenario: Evidence reference

- **WHEN** a trace entry cites code intelligence
- **THEN** it SHALL include repository, indexed commit or graph freshness, query/tool, and symbol UID or structural path when available

### Requirement: End-to-end requirement mapping

Accepted requirements SHALL remain traceable through design, API, implementation plan, coding plan, plan review, test plan, and verification.

#### Scenario: Complete mapping

- **WHEN** verification succeeds
- **THEN** every accepted requirement SHALL map to all applicable downstream artifacts
- **AND** every test-plan item SHALL map back to at least one acceptance criterion

#### Scenario: Missing mapping

- **WHEN** a required downstream mapping is absent
- **THEN** verification SHALL be partial or failed
- **AND** the missing links SHALL be listed

### Requirement: Verification report

The terminal stage SHALL produce a human-readable and machine-readable verification report.

#### Scenario: Report generation

- **WHEN** the workflow reaches verification
- **THEN** it SHALL produce Markdown and JSON reports containing stage outcomes, artifact revisions/digests, evidence freshness, gate decisions, validation flags, blocked items, and overall status

#### Scenario: Human override

- **WHEN** a human accepts an artifact despite a validation flag
- **THEN** the report SHALL show the flag, actor, decision, rationale, and remaining risk

### Requirement: Trace append semantics

Trace storage SHALL be append-only within a workflow run.

#### Scenario: Revision

- **WHEN** an earlier stage is revised
- **THEN** the previous artifact and trace entry SHALL remain addressable
- **AND** the new revision SHALL point to the superseded digest

### Requirement: Correlated observability

Agent and workflow telemetry SHALL be correlated without duplicate lifecycle events.

#### Scenario: Stage span

- **WHEN** a stage executes
- **THEN** its span SHALL contain workflow run ID, ticket ID, stage, artifact digest when available, repository/index commit, and correlation ID
- **AND** secrets or full artifact contents SHALL not be span attributes
