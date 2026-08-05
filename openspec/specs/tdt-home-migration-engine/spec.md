# tdt-home-migration-engine Specification

## Purpose

Define the value-free migration contract that consumes the `tdt-core` provider
kernel for planning and executing filesystem mutations under `$TDT_HOME`.

## Requirements

### Requirement: Migration plans SHALL be typed, bounded, and value-free

The migration engine SHALL validate one source/destination root binding,
generation, provider version, and approved typed relative operations before any
filesystem mutation.

#### Scenario: A valid plan is prepared

- **GIVEN** a plan contains approved relative paths, object classes, hashes,
  ownership/mode attestations, and a unique destination for each operation
- **WHEN** the plan is prepared against matching root identities
- **THEN** the engine records a value-free prepared header
- **AND** it does not include secret values or arbitrary absolute paths

#### Scenario: An unsafe plan is rejected

- **GIVEN** a plan contains an unknown operation, unsafe component, duplicate
  destination, root mismatch, or literal credential value
- **WHEN** the plan is prepared
- **THEN** preparation fails before opening a destination for mutation
- **AND** the diagnostic identifies the logical operation without the value

### Requirement: The executor SHALL remain separately reviewable

The executor MUST accept only the typed `migration_plan`,
`JournalStore`, and explicit source-root mapping. It MUST use the provider
descriptor kernel for all target mutation and retain revision-bound evidence
for each step.

#### Scenario: A strict executor is ready for integration

- **GIVEN** all destination mutations use retained descriptors, no-follow
  checks, synchronization, and root identity verification
- **WHEN** focused execution tests pass against isolated roots
- **THEN** integration may be proposed as a separate reviewed implementation
  step with revision-bound evidence

### Requirement: Strict apply SHALL publish durable per-step effects

The engine SHALL execute only descriptor-relative provider operations and SHALL
publish a contiguous hash-chained record for each legal state transition. The
executor MUST publish `switching`, then one durable `intent` and `completed`
pair for each deterministic plan operation, and MUST reopen the
destination to verify kind, digest, size, mode, ownership, link target, and
root identity before publishing `completed` or `committed`. Descriptor-relative
no-follow staging, rename, and parent synchronization are required;
pathname-based fallbacks are forbidden.

#### Scenario: A regular destination is replaced

- **GIVEN** a staged typed plan and a destination that matches its verified
  backup metadata
- **WHEN** strict apply handles the regular-file operation
- **THEN** it writes an exclusive descriptor-relative staging object, renames
  it below the retained destination parent, synchronizes the parent, and
  reopens the final object before appending `completed`

#### Scenario: A symlink or prior absence is handled

- **GIVEN** a staged operation whose desired object is a relative symlink or
  whose verified backup records prior absence
- **WHEN** apply handles the operation
- **THEN** it uses no-follow inspection and exact link/absence semantics
  without following an external target or deleting a directory

#### Scenario: Destination interference is detected

- **GIVEN** the destination matches neither the recorded pre-state nor the
  desired staged post-state
- **WHEN** an intent is resumed
- **THEN** the executor raises a redacted error and performs no speculative
  replacement

#### Scenario: An operation commits

- **GIVEN** the plan and capability snapshot remain valid
- **WHEN** apply stages, synchronizes, replaces, and verifies one operation
- **THEN** the journal records the transition and the final object identity
- **AND** the parent directory synchronization completes before commit

#### Scenario: A required capability disappears

- **GIVEN** a required no-follow, descriptor-relative, identity, or
  synchronization primitive is unavailable
- **WHEN** apply begins or reaches the affected boundary
- **THEN** it fails closed without a pathname-based fallback
- **AND** any private staging object is removed or recorded
