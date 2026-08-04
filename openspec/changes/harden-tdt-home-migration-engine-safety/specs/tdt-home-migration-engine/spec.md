## MODIFIED Requirements

### Requirement: Compatibility migration entry points SHALL fail closed

Until a strict executor is integrated with the typed root-bound plan and
durable generation journal, compatibility backup, apply, rollback, recovery
persistence, and journal-loading entry points MUST reject mutation rather than
fall back to pathname-based filesystem operations.

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

The typed `migration_plan`, `migration_journal`, and verified backup/staging
surfaces MUST remain separate from the compatibility facade until switching,
recovery, rollback, interruption, and isolated-root evidence have each passed
their own focused tests.

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
