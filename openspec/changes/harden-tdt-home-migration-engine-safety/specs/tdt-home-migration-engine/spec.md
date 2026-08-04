## MODIFIED Requirements

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

The strict executor MUST accept only the typed `migration_plan`,
`JournalStore`, and explicit source-root mapping. It MUST remain separate from
the compatibility facade, use the provider descriptor kernel for all target
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

The strict executor MUST publish `switching`, then one durable `intent` and
`completed` pair for each deterministic plan operation, and MUST reopen the
destination to verify kind, digest, size, mode, ownership, link target, and
root identity before publishing `completed`. Descriptor-relative no-follow
staging, rename, and parent synchronization are required; pathname-based
fallbacks are forbidden.

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

### Requirement: Recovery and rollback SHALL be root-bound and idempotent

Recovery MUST reload and validate the complete generation, plan digest,
hash-chain state, backup manifests, staged payloads, and target root identity
before resuming. Explicit rollback MUST restore only the verified affected
prefix, including regular-file metadata, symlink text, and prior absence.
Repeated recovery or rollback after a terminal state MUST be a no-op, while a
committed generation MUST require a separately approved inverse plan.

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

### Requirement: Interruption evidence SHALL remain synthetic and contained

The interruption harness MUST use temporary approved roots and real child
process `SIGTERM` delivery. It MUST prove that recovery and rollback leave no
unowned migration staging object and do not inspect or mutate the operator's
live `~/.tdt` tree.

#### Scenario: Every durable boundary is exercised

- **GIVEN** the six durable boundaries `prepared`, `staged`, `switching`,
  `intent`, `completed`, and `switched`
- **WHEN** a subprocess is stopped at each boundary and then terminated
- **THEN** fresh-process recovery reaches `committed` for every isolated run
  and the test records only synthetic, value-free evidence
