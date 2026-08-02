# ecosystem-recertification Specification

## Purpose
Certifies that all agent repositories meet the approved contracts from one clean, complete, and reproducibly identified source state before readiness is archived.
## Requirements
### Requirement: Dependency-complete certification

Recertification SHALL remain blocked until every prerequisite remediation change is complete and its evidence is available from current source.

#### Scenario: Prerequisite is incomplete

- **WHEN** any remediation is incomplete, stale, unavailable, or has unresolved security findings
- **THEN** recertification SHALL remain incomplete
- **AND** no archive-ready claim SHALL be emitted

#### Scenario: Prerequisites are complete

- **WHEN** all named remediation changes have current passing evidence
- **THEN** the capstone MAY execute the full matrix against the same source identities

### Requirement: Clean-source matrix

The certification matrix SHALL run from clean checkouts using `uv sync --locked` and SHALL include complete production-source hashes, dependency provenance, public CLI semantics, authorization, authority-policy, artifact-integrity, documentation, quality, and rollback checks.

#### Scenario: All gates pass

- **WHEN** every repository and cross-repository gate passes against one manifest
- **THEN** the manifest SHALL be sufficient to support a readiness decision
- **AND** it SHALL identify commands, fixtures, revisions, results, and sanitized logs

#### Scenario: A gate fails or is skipped

- **WHEN** any required gate fails, is skipped, unavailable, stale, or cannot be attributed to the intended source
- **THEN** certification SHALL fail closed
- **AND** the missing evidence SHALL be named explicitly

### Requirement: No outward mutation

The verification-only capstone SHALL not commit, push, publish, deploy, or archive prerequisite changes as part of certification.

#### Scenario: Verification completes

- **WHEN** the matrix completes
- **THEN** only local sanitized evidence artifacts MAY be produced
- **AND** any release or archive action SHALL require separate explicit authorization

