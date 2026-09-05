# cleanup-archive-verification Specification

## Purpose
This capability preserves trustworthy, value-blind evidence for cleanup work that was archived with operational claims but without durable verification records.

## Requirements

### Requirement: Cleanup verification is durable and value-blind
The system SHALL record the date, target path, command or check identity, result, and non-secret metadata for each corrective verification without recording credentials or raw response bodies.

#### Scenario: Verification succeeds
- **WHEN** a safe corrective check confirms an archived cleanup claim
- **THEN** the evidence register records the target, result, and value-blind metadata

#### Scenario: Verification fails
- **WHEN** a corrective check does not confirm an archived cleanup claim
- **THEN** the evidence register records the failure and does not mark the claim resolved

### Requirement: Manual application work remains explicit
The system SHALL distinguish actual application executable existence and executable metadata from wrapper metadata and SHALL keep manual reinstall work blocked when verification fails.

#### Scenario: Sideloaded executables verify
- **WHEN** both expected application executables exist, are nonempty, and carry executable mode
- **THEN** the evidence records the archived gap as currently resolved without claiming reinstall provenance

#### Scenario: Sideloaded executable is absent
- **WHEN** the wrapper plist exists but an expected executable is absent, empty, or not executable
- **THEN** the evidence records the application as unresolved and retains the user-owned reinstall blocker

### Requirement: Immutable archive history is preserved
The system SHALL place corrective evidence and decisions in a new active change and SHALL NOT modify archived change files or move archived changes back to active.

#### Scenario: Corrective evidence is added
- **WHEN** an archived claim needs remediation
- **THEN** the evidence is written under the corrective change and the original archive remains byte-for-byte untouched

#### Scenario: Archive edit is attempted
- **WHEN** remediation would require changing an archived file
- **THEN** the operation is rejected and the corrective change remains incomplete
