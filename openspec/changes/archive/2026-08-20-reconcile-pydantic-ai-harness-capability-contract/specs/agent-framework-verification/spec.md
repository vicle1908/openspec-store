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

### Requirement: Optional harness dependency ownership is explicit

The workspace SHALL declare an optional harness extra only in a repository that proves a supported production composition seam and a compatible dependency tuple. Consumer repositories without a direct supported use SHALL omit the extra from their root dependency declarations.

#### Scenario: Capability owner retains DynamicWorkflow

- **WHEN** agent-core retains the DynamicWorkflow extra for public typed composition
- **THEN** `build_agent(..., capabilities=[DynamicWorkflow(...)])` SHALL construct and execute a deterministic bounded workflow against the frozen harness tuple
- **AND** public authority validation SHALL classify DynamicWorkflow as runtime authoring and fail closed without the required bounded runtime-authoring grant and audit policy
- **AND** the dependency baseline and documentation SHALL record the resolved Monty version required by that tuple

#### Scenario: Consumer has no direct use

- **WHEN** agent-harness or agent-docs-sync has no production import or behavioral contract for DynamicWorkflow
- **THEN** its root dependency declaration SHALL omit the DynamicWorkflow extra
- **AND** a baseline test SHALL prevent accidental reintroduction

#### Scenario: Documented version conflicts with resolution

- **WHEN** documentation names a Monty version that differs from the resolved lockfile or harness extra requirement
- **THEN** framework verification SHALL fail
- **AND** the conflicting documentation SHALL be corrected before compatibility is accepted
