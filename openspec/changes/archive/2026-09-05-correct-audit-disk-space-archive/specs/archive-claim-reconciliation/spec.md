## Purpose

Provide a durable, value-blind reconciliation record when an archived cleanup change contains stale or ambiguous claims that cannot be corrected by editing immutable archive history.

## ADDED Requirements

### Requirement: Immutable archive preservation
The reconciliation SHALL preserve every file under the referenced archive unchanged and SHALL place all corrective evidence in a separate active change.

#### Scenario: Archived claim needs clarification
- **WHEN** an archived cleanup claim conflicts with later evidence
- **THEN** the corrective change records the clarification without modifying the archived path.

### Requirement: Claim-specific reconciliation
The reconciliation SHALL identify each stale claim, its authoritative later evidence, and the narrowed interpretation that resolves the discrepancy.

#### Scenario: Historical pre-approval statement exists
- **WHEN** an archive says no item was approved or deleted but later evidence records approved cleanup
- **THEN** the reconciliation labels the original statement as pre-approval state and preserves the later action as a separate fact.

### Requirement: Scope and ownership boundaries
The reconciliation SHALL distinguish OpenSpec documentation scope from ownership boundaries for Docker, Trash, package managers, and unrelated workspace changes.

#### Scenario: Unrelated dirty paths exist
- **WHEN** unrelated paths are dirty while the corrective change is prepared
- **THEN** the reconciliation reports them as pre-existing or outside scope and does not modify them to satisfy the correction.

### Requirement: Value-blind evidence
The reconciliation SHALL record paths, statuses, dates, sizes, hashes, and boolean outcomes without credentials, file contents, or raw database records.

#### Scenario: Evidence contains sensitive material
- **WHEN** source evidence could disclose credentials or personal contents
- **THEN** the reconciliation records only a redacted status and metadata needed to verify the claim.
