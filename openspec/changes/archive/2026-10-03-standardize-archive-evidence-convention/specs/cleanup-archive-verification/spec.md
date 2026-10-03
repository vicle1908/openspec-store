# Spec Delta

## MODIFIED Requirements

### Requirement: Immutable archive history is preserved

The system SHALL place corrective evidence and decisions in a new active change and SHALL NOT modify, add files to, remove files from, move, or rewrite archived change files. Adding a file to an archived change directory is a modification and is prohibited. When a violation of this requirement is discovered, the system SHALL record it in a subsequent active change and restore the affected archived directory to its pre-edit state.

#### Scenario: Corrective evidence is added

- **WHEN** an archived claim needs remediation
- **THEN** the evidence is written under the corrective change and the original archive remains byte-for-byte untouched

#### Scenario: Archive edit is attempted

- **WHEN** remediation would require changing an archived file
- **THEN** the operation is rejected and the corrective change remains incomplete

#### Scenario: Archive already holds an added file

- **WHEN** an archived change directory contains a file that was not present when the change was archived
- **THEN** the discrepancy is recorded in a new active change
- **AND** the added file is removed so the archived directory returns to its pre-edit content
- **AND** the recovered content is preserved inside the active corrective change

## ADDED Requirements

### Requirement: Archive evidence uses one standardized form

Changes that perform verification SHALL record their verification evidence in a single `evidence.md` file inside the change directory. Guidance for this artifact SHALL be named in the store's archive operations guidance. The legacy `evidence/` directory form remains valid only for changes already archived with it and SHALL NOT be used for new changes.

#### Scenario: A change records verification evidence

- **WHEN** a change completes verification work before archiving
- **THEN** its evidence is written to `evidence.md` in the change directory
- **AND** the change does not also create an `evidence/` directory

#### Scenario: A change performs no verification

- **WHEN** a change performs no verification work
- **THEN** no evidence artifact is required and the change is not blocked for lacking one

#### Scenario: An existing archive uses the legacy directory form

- **WHEN** an archived change already contains an `evidence/` directory
- **THEN** it is left unchanged and is not migrated, renamed, or converted
