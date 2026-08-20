## ADDED Requirements

### Requirement: Pydantic AI Harness capability acceptance is behavioral and public-boundary based

Every claimed harness capability SHALL have reproducible acceptance evidence executed through the supported public agent boundary, with exact repository identities and dependency import origins.

#### Scenario: Deterministic capability behavior

- **WHEN** a capability is claimed for compaction, reminders, spend, planning, conversation search, advisor, or ToolGuardrail
- **THEN** evidence SHALL execute the relevant behavior with a deterministic in-process model and disposable store
- **AND** import-only or constructibility-only checks SHALL not satisfy the task

#### Scenario: Public boundary mismatch

- **WHEN** a test passes only by constructing an internal runtime or a private upstream helper
- **THEN** the task SHALL remain incomplete
- **AND** a public-boundary regression SHALL be added before acceptance

#### Scenario: Unpriced spend model

- **WHEN** USD spend enforcement is part of the claimed behavior and the test model has no price
- **THEN** the evidence SHALL provide a deterministic price function or configure fail-closed unpriced handling
- **AND** a zero-cost warning SHALL not be counted as budget enforcement

### Requirement: Capability evidence is invalidated by source or dependency drift

Capability completion evidence SHALL be bound to one immutable SHA, raw dirty inventory, content fingerprint, dependency tuple, and imported module origins for every participating repository.

#### Scenario: Covered source changes after a gate

- **WHEN** a covered source, test, lockfile, or dependency import origin changes after a capability gate passes
- **THEN** every dependent task SHALL reopen
- **AND** verification SHALL recapture from the new frozen identity

#### Scenario: Editable dependency is unaccepted

- **WHEN** a consumer imports agent-core or pydantic-ai-harness from a path not included in the accepted identity manifest
- **THEN** cross-repository acceptance SHALL remain incomplete
- **AND** the evidence SHALL identify the contaminated import origin

### Requirement: Archived capability mismatches have corrective ownership

An archived dependency or capability change with incomplete behavior or unsupported completion evidence SHALL be referenced by an active corrective ledger and SHALL remain unchanged.

#### Scenario: Archived mismatch is found

- **WHEN** current verification finds an archived harness task whose behavior or evidence is incomplete
- **THEN** the corrective ledger SHALL identify the archived path, task, current source evidence, owning corrective change, and closure gate
- **AND** the archived artifact SHALL not be rewritten

#### Scenario: Corrective change overlaps active work

- **WHEN** a corrective task overlaps an existing active change
- **THEN** exactly one change SHALL own implementation
- **AND** the other change SHALL cross-reference it without duplicating ownership
