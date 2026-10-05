# Spec Delta

## ADDED Requirements

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
