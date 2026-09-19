# archive-closure-audit Specification

## Purpose
Provide an immutable, evidence-backed reconciliation of archived cloud-drive task ledgers whose completion claims exceed directly supported execution evidence.

## Requirements

### Requirement: Archive claims require execution evidence

The audit SHALL compare each claimed non-iCloud mutation with exact target paths, authorization, and before/after evidence.

#### Scenario: Mutation claim lacks exact approval

- **WHEN** an archived task claims Google Drive or Desktop/Documents deletion without an exact approval and target manifest
- **THEN** the audit classifies the claim as unsupported or performed-but-unverifiable based on observed path state and SHALL NOT execute or authorize the mutation.

### Requirement: Archived history is immutable

The audit SHALL write reconciliation evidence only to the active corrective change and SHALL NOT edit, move, or rewrite archived files.

#### Scenario: Historical ledger conflicts with evidence

- **WHEN** an archived ledger conflicts with later evidence
- **THEN** the audit records the conflict with paths and task identifiers while preserving the archive byte-for-byte.

### Requirement: Sensitive data is excluded

The audit SHALL record only value-blind metadata such as paths, task identifiers, counts, timestamps, hashes, statuses, and exit codes.

#### Scenario: Candidate path contains personal or credential-bearing data

- **WHEN** evidence references a sensitive path
- **THEN** the audit records classification and metadata without contents or secrets.
