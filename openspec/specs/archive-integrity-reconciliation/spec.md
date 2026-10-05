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

### Requirement: Immutability violations are recorded and reverted

The reconciliation SHALL treat any file present in an archived change directory that was not part of the archived content as a violation. It SHALL record the violation with the archive path, the offending path, and the commit or reference that introduced it, and SHALL revert the archived directory to its pre-edit content. Reversion SHALL restore the archive without introducing any further change to archived bytes beyond removing the offending addition.

#### Scenario: An added file is found in an archived change

- **WHEN** reconciliation finds a file inside an archived change directory that is not part of the archived content
- **THEN** it records the archive path, the offending path, and the introducing reference
- **AND** it removes the added file so the archived directory matches its pre-edit content
- **AND** it preserves the recovered content in a new active change

#### Scenario: An archived file was edited in place

- **WHEN** reconciliation finds that a file belonging to the archived change has different content than the archived revision
- **THEN** it records the discrepancy with the path and the reference
- **AND** it restores the archived content from the recorded revision
- **AND** the corrective change remains incomplete until the archive matches its archived revision

#### Scenario: The violating commit is not recoverable

- **WHEN** the reference that introduced the violation cannot be identified
- **THEN** the reconciliation records the violation as unresolved with the observable evidence
- **AND** it SHALL NOT guess at the original content or delete an ambiguous file

### Requirement: Corrective evidence reconciles stale archive claims

A corrective change addressing an archived completion claim SHALL identify the affected archived tasks, distinguish verified behavior from unsupported or degraded evidence, and record the current release conditions without changing archived files.

#### Scenario: Archived task overstates current implementation
- **WHEN** a checked archived task conflicts with current source, roster, or execution evidence
- **THEN** the corrective record SHALL identify the task and discrepancy
- **AND** it SHALL leave the archived task and evidence files unchanged

#### Scenario: Current evidence is degraded
- **WHEN** a live apply or verification run contains an updater failure, unknown channel currency, or bounded measurement limitation
- **THEN** the corrective record SHALL preserve that outcome
- **AND** it MUST NOT claim a clean baseline or complete currency proof

### Requirement: Corrective evidence is value-blind and reproducible

Corrective evidence SHALL use paths, task identifiers, line references, counts, statuses, hashes, and boolean outcomes sufficient to reproduce the review while excluding credentials, tokens, environment values, personal contents, and raw database records.

#### Scenario: Configuration contains sensitive values
- **WHEN** a provenance or schedule inspection reads a configuration containing secret-bearing values
- **THEN** the evidence SHALL record only the key names and safe metadata
- **AND** it MUST omit the values

#### Scenario: Archive immutability is checked
- **WHEN** the corrective change is verified before implementation or archive closure
- **THEN** the check SHALL confirm that no archived path was modified by the corrective planning work
- **AND** any discrepancy SHALL block a clean readiness claim
