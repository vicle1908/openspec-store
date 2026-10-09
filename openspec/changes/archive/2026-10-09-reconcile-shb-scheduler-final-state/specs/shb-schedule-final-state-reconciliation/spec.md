# Spec Delta: shb-schedule-final-state-reconciliation

## Purpose

This capability preserves the completed scheduler archive while reconciling final implementation evidence, canonical scheduler specifications, and operator-facing documentation with the live system state.

## ADDED Requirements

### Requirement: Immutable Archive Preservation
The reconciliation process MUST NOT modify, move, delete, or re-archive files under the completed scheduler archive.

#### Scenario: Archive remains unchanged
- **WHEN** the corrective change is applied
- **THEN** every file under `openspec/changes/archive/2026-10-09-containerize-shb-scheduler-postgres18/` MUST remain unchanged
- **AND** the archive path MUST remain present

### Requirement: Final-State Evidence Reconciliation
The corrective record MUST identify the final scheduler and skills repository revisions, distinguish historical evidence from final-state verification, and report command outcomes without secrets or raw database records.

#### Scenario: Final implementation identity is recorded
- **WHEN** the live scheduler and skills repositories are inspected
- **THEN** the corrective evidence MUST record their immutable commit identities, working-tree status, and verification command outcomes
- **AND** it MUST identify any earlier archive evidence that predates the final implementation

#### Scenario: Unsupported historical claims are not promoted
- **WHEN** archived review or evidence text conflicts with later implementation facts
- **THEN** the corrective record MUST preserve the historical text as historical
- **AND** it MUST NOT claim that the earlier review observed later hardening

### Requirement: Canonical Specification Strict Conformance
The canonical `shb-schedule-engine` specification MUST preserve scheduler behavior and scenarios while satisfying strict OpenSpec validation.

#### Scenario: Strict validation succeeds
- **WHEN** `openspec validate shb-schedule-engine --strict --json --store openspec-store` is run
- **THEN** the command MUST exit successfully with no requirement-length warning
- **AND** the scheduler behavior represented by the specification MUST remain unchanged

### Requirement: Operator Documentation Consistency
Curated SHB scheduler documentation MUST describe Docker Compose/PostgreSQL operation, PostgreSQL advisory-lock ownership for container deployments, and local SQLite fallback without retaining obsolete host-service installation guidance.

#### Scenario: Wiki matches implementation
- **WHEN** an operator reads the scheduler wiki entities
- **THEN** they MUST find Docker Compose startup, PostgreSQL persistence, and container ownership guidance
- **AND** they MUST NOT be instructed to install or operate the removed LaunchAgent/systemd scheduler generators

### Requirement: Bounded Host Artifact Cleanup
Cleanup MUST be limited to the explicitly approved obsolete scheduler LaunchAgent plist and residual scheduler bytecode directory, with exact-path verification before and after removal.

#### Scenario: Obsolete scheduler plist is removed
- **WHEN** the exact plist path is verified and no active scheduler process depends on it
- **THEN** only `~/Library/LaunchAgents/com.shb.schedule.plist` MUST be removed
- **AND** unrelated LaunchAgent files MUST remain untouched

#### Scenario: Residual cache is removed
- **WHEN** `src/shb_schedule/service/` is verified to contain no source files and only residual bytecode
- **THEN** only that residual scheduler cache directory MUST be removed
- **AND** scheduler source directories MUST remain intact
