## ADDED Requirements

### Requirement: Documentation write containment

All documentation and OpenSpec write tools SHALL enforce configured workspace-relative roots at the tool boundary in addition to any prompt guard or hook.

#### Scenario: Contained write

- **WHEN** an authorized and approved write resolves inside an allowed root
- **THEN** the tool SHALL perform the requested write
- **AND** the audit event SHALL record the normalized target

#### Scenario: Traversal escape

- **WHEN** a target uses `..`, an absolute path, or a symlink to resolve outside all allowed roots
- **THEN** the tool SHALL reject the write before creating directories or files
- **AND** the rejection SHALL be audited

#### Scenario: Missing write policy

- **WHEN** a write-capable agent has no effective allowed-root policy
- **THEN** agent construction SHALL fail before the model can request the tool
- **AND** the write tool SHALL still fail closed if run-scoped policy is later absent

#### Scenario: Approval is not containment

- **WHEN** an out-of-root target is approved
- **THEN** the containment policy SHALL still reject it

### Requirement: Asynchronous durable docs workflow

The supported docs-sync LangGraph pipeline SHALL execute asynchronous handlers through the asynchronous graph API and SHALL keep its checkpointer resource alive through run or resume completion.

#### Scenario: Non-durable run

- **WHEN** `docs-sync sync` runs without `--durable`
- **THEN** the graph SHALL execute through `ainvoke` or `astream`
- **AND** async handlers SHALL not be wrapped in synchronous `invoke` on a worker thread

#### Scenario: Durable run

- **WHEN** `docs-sync sync --durable` runs
- **THEN** the runner SHALL enter the checkpointer context before graph compilation
- **AND** it SHALL exit the context only after the graph run completes
- **AND** a stable `thread_id` SHALL identify checkpoints

#### Scenario: Resume after interruption

- **WHEN** a durable run is interrupted after a completed node
- **THEN** a new runner SHALL resume from the stored checkpoint
- **AND** completed side-effecting nodes SHALL not be repeated

### Requirement: Integration tests fail on integration errors

Tests that claim to verify guardrails, delegation, DynamicWorkflow, or durability SHALL fail when construction or execution fails for reasons other than an explicitly asserted error.

#### Scenario: Construction error

- **WHEN** a configured integration cannot construct
- **THEN** the test SHALL report the exception
- **AND** it SHALL not use an unconditional `except Exception: pass`

#### Scenario: Optional dependency skip

- **WHEN** an optional dependency is intentionally absent
- **THEN** the skip condition SHALL distinguish absence from an installed-but-incompatible version

#### Scenario: Enabled integration is installed

- **WHEN** the reviewed lockfile installs a configured integration
- **THEN** its integration test SHALL execute
- **AND** zero tests SHALL skip because that integration failed to import or construct
