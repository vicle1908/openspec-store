## ADDED Requirements

### Requirement: OpenSpec operation guidance is current and subordinate
The repository SHALL provide project-specific apply and archive guidance through
the current OpenSpec operation-guidance fields. The guidance MUST remain
advisory, MUST NOT replace repository instructions or verification gates, and
MUST be delivered separately from artifact-content rules and task state.

#### Scenario: Apply instructions are requested
- **WHEN** an agent requests apply instructions for a change
- **THEN** it receives current project context and apply guidance that requires preserving existing work, reading applicable repository guidance, and running focused verification before task completion

#### Scenario: Archive instructions are requested
- **WHEN** an agent requests archive instructions for a change
- **THEN** it receives current project context and archive guidance covering explicit approval, implementation verification, strict validation, evidence boundaries, and readiness-claim limits

#### Scenario: Advisory guidance conflicts with controlling state
- **WHEN** operation guidance conflicts with the selected root, built-in workflow state, an explicit user decision, or repository policy
- **THEN** the agent preserves the controlling value, reports the conflict, and does not treat the advisory text as authorization

### Requirement: OpenSpec authoring guidance classifies spec impact explicitly
OpenSpec guidance SHALL permit `skip_specs: true` only when a change has no
spec-level behavior impact and SHALL require capability deltas for changes to
agent behavior, instruction governance, generated workflow contracts, CI
enforcement, or externally relied-on tooling behavior. Guidance MUST require a
meaningful Purpose section for a delta that introduces a new capability.

#### Scenario: Pure internal refactor has no spec impact
- **WHEN** a proposed change alters no observable or governed behavior
- **THEN** guidance permits `skip_specs: true`, requires no delta spec files, and treats the skipped specs artifact as satisfied

#### Scenario: Governance or workflow behavior changes
- **WHEN** a change alters agent instructions, workflow safety, generated delivery, validation, or CI enforcement
- **THEN** guidance rejects `skip_specs: true` and requires deltas for every affected capability

#### Scenario: New capability delta is authored
- **WHEN** a delta spec introduces a capability that has no main spec
- **THEN** guidance requires a useful Purpose of at least the strict-validation minimum so archive can create a complete main spec without a placeholder

### Requirement: Archive guidance prevents in-flight sync races
Generated archive and bulk-archive guidance MUST fetch current archive inputs
and applicable spec rules before writes, MUST complete requested semantic sync
synchronously, and MUST verify the resulting main specs before moving any
change directory. A failed lookup, sync, or verification SHALL stop the
archive without claiming success.

#### Scenario: Archive includes delta synchronization
- **WHEN** a user approves synchronization while archiving a change with delta specs
- **THEN** sync finishes inline, the main specs are verified against the delta, and only then may the change directory move to the archive

#### Scenario: Required instruction lookup fails
- **WHEN** archive or sync cannot obtain valid current archive inputs or spec rules
- **THEN** it stops before writing a main spec or moving a change and reports the failed lookup

#### Scenario: A generated archive skill delegates sync in the background
- **WHEN** validation finds guidance that permits a change to move while its spec sync remains in flight
- **THEN** validation fails and identifies the unsafe generated surface
