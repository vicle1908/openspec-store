# tdt-home-migration-engine Specification

## Purpose

Define the value-free, journaled migration contract that consumes the
`tdt-core` provider kernel while keeping planning and recovery safe to test
before any operator cutover.

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

### Requirement: Compatibility migration entry points SHALL fail closed

Compatibility backup, apply, rollback, recovery persistence, and
journal-loading entry points MUST remain fail-closed and MUST NOT delegate
authority to arbitrary caller-supplied paths. The separately reviewable strict
executor is the only API allowed to perform a typed, root-bound migration.

#### Scenario: A compatibility mutator is called

- **GIVEN** a caller supplies an explicit synthetic source, target, backup, or
  journal path to the compatibility API
- **WHEN** the caller invokes backup, apply, rollback, save, or load
- **THEN** the API fails closed with a redacted `ApplyError`
- **AND** it does not create, replace, remove, or copy any filesystem object

#### Scenario: The compatibility module is inspected for fallback behavior

- **GIVEN** the provider security contract requires descriptor-relative
  mutation
- **WHEN** the migration compatibility module is loaded or reviewed
- **THEN** it contains no `shutil`, pathname `os.replace`, recursive pathname
  deletion, or implicit private-directory creation fallback

### Requirement: The strict executor SHALL remain separately reviewable

The strict executor MUST accept only the typed migration plan, `JournalStore`,
and explicit source-root mapping. It MUST remain separate from the
compatibility facade, use the provider descriptor kernel for all target
mutation, and retain revision-bound evidence for switching, recovery,
rollback, interruption, and isolated-root verification.

#### Scenario: Partial implementation is present

- **GIVEN** planning, journaling, or backup/staging is implemented but strict
  switching or recovery is not
- **WHEN** the compatibility API is used
- **THEN** it remains read-only or fail-closed
- **AND** the incomplete executor is not represented as an archived completion

#### Scenario: A strict executor is ready for integration

- **GIVEN** all destination mutations use retained descriptors, no-follow
  checks, synchronization, and root identity verification
- **WHEN** focused interruption and rollback tests pass against isolated roots
- **THEN** integration may be proposed as a separate reviewed implementation
  step with revision-bound evidence

### Requirement: Strict apply SHALL publish durable per-step effects

The engine SHALL execute only descriptor-relative provider operations and SHALL
publish a contiguous hash-chained record for each legal state transition. The
strict executor SHALL publish `switching`, then one durable `intent` and
`completed` pair for each deterministic plan operation. It MUST reopen each
destination to verify kind, digest, size, mode, ownership, link target, and
root identity before publishing `completed` or `committed`.

#### Scenario: An operation commits

- **GIVEN** the plan and capability snapshot remain valid
- **WHEN** apply stages, synchronizes, replaces, and verifies one operation
- **THEN** the journal records the transition and the final object identity
- **AND** the parent directory synchronization completes before commit

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
- **WHEN** apply or rollback handles the operation
- **THEN** it uses no-follow inspection and exact link/absence semantics
  without following an external target or deleting a directory

#### Scenario: Destination interference is detected

- **GIVEN** the destination matches neither the recorded pre-state nor the
  desired staged post-state
- **WHEN** an intent is resumed
- **THEN** the executor raises a redacted error and performs no speculative
  replacement

#### Scenario: A required capability disappears

- **GIVEN** a required no-follow, descriptor-relative, identity, or
  synchronization primitive is unavailable
- **WHEN** apply begins or reaches the affected boundary
- **THEN** it fails closed without a pathname-based fallback
- **AND** any private staging object is removed or recorded for recovery

### Requirement: Recovery and rollback SHALL be root-bound and idempotent

Recovery SHALL validate the complete journal and legal state transitions before
resuming, including the plan digest, hash-chain state, verified generation
manifests, staged payloads, and target root identity. Explicit rollback MUST
restore only the verified affected prefix, including regular-file metadata,
symlink text, and prior absence. Repeated recovery or rollback after a
terminal state MUST be a no-op, while a committed generation MUST require a
separately approved inverse plan.

#### Scenario: Recovery resumes after interruption

- **GIVEN** a synthetic interruption leaves a valid journal in an intermediate
  state
- **WHEN** recovery is run against the same root identities
- **THEN** it completes or safely rolls back the approved operation
- **AND** a second recovery run is a no-op with the same terminal result

#### Scenario: Fresh-process recovery follows SIGTERM

- **GIVEN** a child process is terminated after any durable boundary from
  `prepared` through `switched`
- **WHEN** a fresh executor calls `recover` with the same generation and
  explicit source root
- **THEN** it converges to one verified `committed` state without duplicating
  completed effects or journal records

#### Scenario: Rollback restores the captured state

- **GIVEN** an interrupted nonterminal generation with verified backup
  metadata
- **WHEN** explicit rollback is requested
- **THEN** the destination returns to its prior regular, symlink, or absent
  state and a second rollback is a no-op

#### Scenario: Journal integrity fails

- **GIVEN** a journal record is missing, reordered, truncated, or hash-modified
- **WHEN** recovery or rollback starts
- **THEN** the engine refuses to mutate either root
- **AND** it reports only the journal identity and failing sequence metadata

### Requirement: Interruption evidence SHALL remain synthetic and contained

The test harness SHALL use temporary approved roots, value-free fixtures, and
real child-process `SIGTERM` delivery. It SHALL inject deterministic failures
at every migration transaction boundary and prove fixture containment and
cleanup. It MUST NOT inspect or mutate the operator's live `~/.tdt` tree.

#### Scenario: Boundary faults are exercised

- **GIVEN** a temporary approved test anchor and a value-free legacy fixture
- **WHEN** the harness injects a fault before and after each boundary
- **THEN** every run reaches a classified recoverable or rolled-back state
- **AND** no test opens or mutates the real `~/.tdt`

#### Scenario: Every durable boundary is exercised

- **GIVEN** the six durable boundaries `prepared`, `staged`, `switching`,
  `intent`, `completed`, and `switched`
- **WHEN** a subprocess is stopped at each boundary and then terminated
- **THEN** fresh-process recovery reaches `committed` for every isolated run
  and the test records only synthetic, value-free evidence

#### Scenario: Staging cleanup is verified

- **GIVEN** a fault occurs during staging or replacement
- **WHEN** the synthetic run terminates
- **THEN** no unowned staging file, descriptor, or out-of-root object remains
- **AND** the failure evidence contains no secret-shaped value
