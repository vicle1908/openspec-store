# Spec Delta

## Purpose

Defines bounded growth and recovery obligations for Git-backed snapshot stores, so that
continuously appended version history cannot grow without limit and any reclamation preserves
the store's ability to serve its owning tool.

## ADDED Requirements

### Requirement: Snapshot stores declare a size ceiling

A Git-backed snapshot store under the workstation SHALL declare a measurable size ceiling, and
SHALL be reported when its on-disk size exceeds that ceiling, distinguishing loose objects from
packed objects in the measurement.

#### Scenario: Store exceeds its ceiling

- **WHEN** a snapshot store's total on-disk size exceeds its declared ceiling
- **THEN** the report SHALL state the exceeded ceiling, the total size, and the loose-versus-
  packed object split
- **AND** it SHALL identify the object count and the commit count contributing to the excess

#### Scenario: Store is within its ceiling

- **WHEN** a snapshot store's total on-disk size is at or below its declared ceiling
- **THEN** the report SHALL record it as within bounds
- **AND** no reclamation SHALL be proposed

### Requirement: Accumulated loose objects are bounded

A snapshot store MUST NOT rely on loose Git objects as its steady state. Where loose objects
account for substantially more space than the packed representation of the same history, the
store SHALL be repacked by its owning tool command.

#### Scenario: Loose objects dominate the store

- **WHEN** a snapshot store's loose objects account for a material majority of its size while
  the equivalent packed history is a small fraction of it
- **THEN** the report SHALL classify the loose objects as reclaimable-by-repack
- **AND** it SHALL name the owner command that performs the repack rather than proposing direct
  deletion of the object files

#### Scenario: Repack does not complete

- **WHEN** a repack fails or is interrupted
- **THEN** the existing objects SHALL remain intact and the store SHALL remain readable
- **AND** the workflow MUST NOT fall back to deleting object files directly

### Requirement: Reclamation preserves store integrity and recoverability

Reclaiming space from a snapshot store SHALL preserve the store's ability to serve its owning
tool, and SHALL be reversible or evidenced to the extent the store's purpose requires.

#### Scenario: Store remains readable after reclamation

- **WHEN** space is reclaimed from a snapshot store
- **THEN** the owning tool SHALL still open the store and the most recent snapshot SHALL remain
  retrievable
- **AND** the reclamation SHALL be recorded with before and after measurements

#### Scenario: History depth is reduced

- **WHEN** reclamation would reduce retained history depth rather than only repack it
- **THEN** that action SHALL require separate operator authorization
- **AND** the retained depth before and after SHALL be recorded

### Requirement: Growth bounds are enforced by a repeatable owner command

Enforcement of a snapshot store's growth bounds SHALL be performed by a declared, repeatable
command belonging to the owning tool or the workstation maintenance pipeline, so that bounds are
maintained rather than corrected once.

#### Scenario: Bounds are enforced on schedule

- **WHEN** the workstation maintenance pipeline runs
- **THEN** it SHALL evaluate each declared snapshot store against its ceiling
- **AND** it SHALL report the outcome without requiring manual measurement

#### Scenario: Enforcement is unavailable

- **WHEN** the owning tool for a snapshot store cannot perform the repack
- **THEN** the report SHALL record the store as exceeding bounds with the owner command
  unavailable
- **AND** it MUST NOT substitute a broad recursive deletion
