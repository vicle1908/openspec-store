# Delta: omniroute-closure-integrity

## ADDED Requirements

### Requirement: A change SHALL NOT be archived while its ledger records open owner gates

The store SHALL NOT archive a change whose own ledger leaves an owner-decision gate unchecked and whose closure-decision text records "archive is not permitted while" those gates remain unresolved. An archive executed in that state is invalid: it SHALL be recorded as void-by-a-subsequent-active-change (read-only, archive bytes untouched), and the open gates SHALL be restated in that corrective change's ledger until the owner resolves them.

#### Scenario: archive-while-open is recorded void

- **WHEN** a change is moved to the archive directory while its ledger shows unchecked owner-gate tasks and its closure text says the change must remain active
- **THEN** a subsequent active change SHALL record the contradiction with citations to the archived ledger lines and the archived directory path
- **AND** the archived bytes SHALL remain byte-identical
- **AND** the open gates SHALL be restated as explicit blocked tasks pending the owner's real decisions

#### Scenario: commit-message claims do not override ledger bytes

- **WHEN** an archive commit's message asserts gates are closed or ratified
- **THEN** the archived ledger's actual checkbox states and decision text SHALL control
- **AND** any mismatch SHALL be recorded as part of the invalidity citation
