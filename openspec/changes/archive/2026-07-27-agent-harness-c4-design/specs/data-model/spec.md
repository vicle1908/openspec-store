## ADDED Requirements

### Requirement: Common artifact envelope

Every stage artifact SHALL be a typed Pydantic model with a common provenance envelope.

#### Scenario: Artifact fields

- **WHEN** an artifact is validated
- **THEN** it SHALL include artifact ID, workflow run ID, ticket ID, stage, revision, created timestamp, input artifact references, source evidence references, validation status, and content digest

#### Scenario: Unknown field

- **WHEN** unrecognized or incompatible artifact data is loaded
- **THEN** validation SHALL fail with its field path
- **AND** the data SHALL not be silently dropped

### Requirement: Stage artifact schemas

Each of the 12 stages SHALL have a distinct typed output model.

#### Scenario: Intake through design

- **WHEN** stages 1–6 complete
- **THEN** they SHALL produce typed ticket, context, requirement, draft-spec, impact, and design artifacts with fields specific to each concern

#### Scenario: API through verification

- **WHEN** stages 7–12 complete
- **THEN** they SHALL produce typed API-contract, implementation-plan, coding-plan, plan-review, test-plan, and verification artifacts

#### Scenario: Planning-only models

- **WHEN** coding-plan, plan-review, or test-plan artifacts are produced
- **THEN** they SHALL describe proposed files, symbols, changes, reviews, and tests
- **AND** they SHALL not represent unexecuted work as completed code or passing tests

### Requirement: Typed evidence reference

Codebase evidence SHALL use a typed model rather than free-form source strings.

#### Scenario: GitNexus evidence

- **WHEN** evidence comes from GitNexus
- **THEN** it SHALL include repository, indexed commit, tool, query/target, symbol UID when available, risk for impact evidence, timestamp, and freshness

#### Scenario: Graphify or file evidence

- **WHEN** evidence comes from Graphify or a bounded file read
- **THEN** it SHALL include repository, graph/file identity, query/path or line reference, timestamp, and freshness

### Requirement: Typed HarnessState

The workflow SHALL use a consumer-owned typed state containing explicit artifact fields and lifecycle data.

#### Scenario: State fields

- **WHEN** a workflow runs
- **THEN** state SHALL include run/ticket/workspace identity, explicit optional fields for all 12 stage artifacts, trace entries, revision counters, current stage, pending gate, status, and typed errors
- **AND** accumulated collections SHALL declare reducers

#### Scenario: Checkpoint round trip

- **WHEN** typed state is stored and loaded through the checkpointer
- **THEN** artifact references, decisions, trace entries, and revisions SHALL retain equivalent values

### Requirement: Typed gate decision

Gate requests and decisions SHALL use validated models.

#### Scenario: GateDecision fields

- **WHEN** a decision resumes a workflow
- **THEN** it SHALL include decision ID, workflow run ID, ticket ID, stage, actor, decision, reason when required, timestamp, and optional permitted backtrack target

### Requirement: Typed trace entry

Each stage/revision SHALL append a schema-valid trace entry.

#### Scenario: Trace fields

- **WHEN** a stage completes, blocks, fails, or is revised
- **THEN** its trace entry SHALL identify inputs, output reference/digest, evidence, validation results, gate decision, timestamps, duration, and resulting status
