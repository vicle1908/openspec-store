# archive-integrity-reconciliation Specification

## Purpose
Provide an immutable, evidence-backed reconciliation record when an archived OpenSpec task ledger claims completion beyond directly verified implementation evidence.

## Requirements

### Requirement: Archived ledgers remain immutable

The reconciliation SHALL treat archived change files as read-only historical records and SHALL write all corrections only to a new active change.

#### Scenario: Archived ledger overstates completion

- **WHEN** an archived task ledger contains checked tasks that conflict with active-state evidence
- **THEN** the reconciliation records the discrepancy without editing or moving the archived directory.

### Requirement: Unresolved gates are reopened explicitly

The reconciliation SHALL identify each unsupported checked task and record its release condition as blocked, pending exact evidence or explicit authorization.

#### Scenario: Approval-gated mutation lacks evidence

- **WHEN** a checked task requires a cloud, personal-data, or filesystem mutation without exact approval and post-action evidence
- **THEN** the reconciliation classifies that task as unresolved and preserves it as unchecked in the corrective ledger.

### Requirement: Verification blockers remain truthful

The reconciliation SHALL preserve known failed or unproven verification outcomes instead of treating partial checks as full completion.

#### Scenario: Full test gate terminates abnormally

- **WHEN** a full-suite task has a known nonzero termination and no approved exclusion policy
- **THEN** the reconciliation records the task as blocked and SHALL NOT claim a green full-suite result.

### Requirement: Evidence is value-blind

The reconciliation SHALL record paths, task identifiers, counts, hashes, statuses, and line references without recording credentials, tokens, personal file contents, or raw database records.

#### Scenario: Evidence contains sensitive source material

- **WHEN** a source artifact includes secret-bearing or personal content
- **THEN** the reconciliation records only a redacted classification and metadata needed to reproduce the check.
