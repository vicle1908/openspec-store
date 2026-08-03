# TDT_HOME Migration Engine Specification

## Purpose

Define the value-free, journaled migration contract that consumes the
`tdt-core` provider kernel while keeping planning and recovery safe to test
before any operator cutover.

## ADDED Requirements

### Requirement: Migration plans SHALL be typed, bounded, and value-free

The migration engine SHALL validate one source/destination root binding,
generation, provider version, and allowlisted relative operations before any
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

### Requirement: Apply SHALL use a hash-chained journal and provider kernel

The engine SHALL execute only descriptor-relative provider operations and SHALL
publish a contiguous hash-chained record for each legal state transition.

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
- **AND** any private staging object is removed or recorded for recovery

### Requirement: Recovery and rollback SHALL be idempotent and tamper-evident

Recovery SHALL validate the complete journal and legal state transitions before
resuming, while rollback SHALL use recorded inverse operations only.

#### Scenario: Recovery resumes after interruption

- **GIVEN** a synthetic interruption leaves a valid journal in an intermediate
  state
- **WHEN** recovery is run against the same root identities
- **THEN** it completes or safely rolls back the approved operation
- **AND** a second recovery run is a no-op with the same terminal result

#### Scenario: Journal integrity fails

- **GIVEN** a journal record is missing, reordered, truncated, or hash-modified
- **WHEN** recovery or rollback starts
- **THEN** the engine refuses to mutate either root
- **AND** it reports only the journal identity and failing sequence metadata

### Requirement: Synthetic interruption testing SHALL be isolated from live roots

The test harness SHALL inject deterministic failures at every migration
transaction boundary and SHALL prove fixture containment and cleanup.

#### Scenario: Boundary faults are exercised

- **GIVEN** a temporary approved test anchor and a value-free legacy fixture
- **WHEN** the harness injects a fault before and after each boundary
- **THEN** every run reaches a classified recoverable or rolled-back state
- **AND** no test opens or mutates the real `~/.tdt`

#### Scenario: Staging cleanup is verified

- **GIVEN** a fault occurs during staging or replacement
- **WHEN** the synthetic run terminates
- **THEN** no unowned staging file, descriptor, or out-of-root object remains
- **AND** the failure evidence contains no secret-shaped value
