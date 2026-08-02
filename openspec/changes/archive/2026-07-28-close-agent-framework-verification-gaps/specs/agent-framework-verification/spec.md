## ADDED Requirements

### Requirement: Corrective completion ledger

The workspace SHALL maintain an evidence-backed ledger for every archived completion claim found inconsistent with active specifications or implementation, without rewriting the archived record.

#### Scenario: Archived completion mismatch

- **WHEN** verification finds an archived task whose required behavior or evidence is incomplete
- **THEN** an active corrective task SHALL identify the archived task, current evidence, owning change, and required closure evidence
- **AND** the archived artifact SHALL remain unchanged

#### Scenario: Overlapping active change

- **WHEN** a corrective item overlaps an active change
- **THEN** exactly one active task SHALL own implementation
- **AND** the other change SHALL cross-reference that task rather than duplicate ownership

### Requirement: Evidence-gated task completion

A corrective task SHALL remain incomplete until its required behavior and verification evidence are both reproducible from the current source state.

#### Scenario: Required gate passes

- **WHEN** a task requires OpenSpec validation, formatting, linting, type checking, tests, compatibility analysis, restart verification, deployment inspection, or rollback evidence
- **THEN** the evidence manifest SHALL record the command, repository, relevant environment or fixture, result, and reproducible source identity
- **AND** the task MAY be marked complete only when every required gate passes

#### Scenario: Dirty source identity

- **WHEN** verification runs with tracked or untracked worktree changes
- **THEN** source identity SHALL include the repository `HEAD`, a hash of the tracked binary diff, and a sorted untracked-path inventory
- **AND** a commit hash alone SHALL NOT be accepted as the verified source state

#### Scenario: Required gate is skipped or unavailable

- **WHEN** a required gate is skipped, unavailable, stale, or fails
- **THEN** the owning task SHALL remain incomplete
- **AND** the blocker SHALL be recorded without substituting unit-test success for the missing evidence

#### Scenario: Later change invalidates evidence

- **WHEN** covered source, checkpoint semantics, planning requirements, deployment artifacts, or required backend assumptions change after a gate was recorded
- **THEN** every dependent completion and archive task SHALL be reopened
- **AND** the overlapping active change SHALL remain the sole implementation owner
- **AND** the corrective change SHALL consume refreshed evidence rather than duplicate implementation

### Requirement: Cross-repository compatibility gate

`agent-core`, `agent-docs-sync`, and `agent-harness` SHALL be verified together against the declared direct Pydantic AI, Pydantic AI Harness, and LangGraph compatibility matrix. The baseline SHALL use the frozen repository lockfiles, and the candidate row SHALL be a disposable fresh resolution within the existing declared dependency bounds.

#### Scenario: Framework boundary changes

- **WHEN** implementation changes lifecycle hooks, memory composition, agent construction, workflow routing, gates, checkpointers, or native graph validation
- **THEN** all three repository contract suites SHALL run against the same declared framework versions
- **AND** private upstream imports or attributes SHALL fail the gate

#### Scenario: Candidate resolution matches baseline

- **WHEN** the disposable candidate resolution produces the same framework versions as the frozen lockfiles
- **THEN** the evidence SHALL record that the matrix collapsed to one version tuple
- **AND** the candidate gate SHALL NOT claim coverage of an unavailable version

#### Scenario: Compatibility projection removal

- **WHEN** a legacy hook, memory, builder, or workflow projection is proposed for removal
- **THEN** production-caller analysis SHALL show no remaining caller
- **AND** rollback and migration instructions SHALL be verified before removal

### Requirement: High-risk change containment

HIGH or CRITICAL workflow-root changes SHALL be implemented incrementally behind characterization and negative-path tests.

#### Scenario: Critical root modification

- **WHEN** GitNexus rates an affected symbol HIGH or CRITICAL
- **THEN** its affected processes SHALL be listed in change evidence
- **AND** characterization tests SHALL pass before and after the modification
- **AND** post-change detection SHALL confirm that only intended symbols and processes changed
