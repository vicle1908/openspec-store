# tdt-home-live-cutover Specification

## Purpose
Define the explicit approval, execution, recovery, and evidence contract for a
future cutover of the operator-owned `~/.tdt` root.
## Requirements
### Requirement: Live cutover SHALL require complete preflight approval

Execution SHALL require provider, source-conformance, synthetic-recovery, and
rollout evidence plus a current root snapshot, concrete mapping, owners,
principals, maintenance window, and rollback decision.

#### Scenario: Preflight is complete

- **GIVEN** every prerequisite evidence scope is green or explicitly accepted
  with a bounded exception
- **AND** the root snapshot and mapping contain no unknown or secret-bearing
  input
- **WHEN** the authorized operator reviews the cutover plan
- **THEN** the plan becomes eligible for the stated maintenance window
- **AND** eligibility is not execution approval until separately recorded

#### Scenario: A prerequisite is missing

- **GIVEN** any consumer, principal, mapping, backup, or recovery fact is
  missing, contradictory, or stale
- **WHEN** the cutover plan is evaluated
- **THEN** execution remains blocked
- **AND** no live path, link, permission, schedule, or database is changed

### Requirement: Cutover execution SHALL be quiesced and descriptor-relative

Execution SHALL quiesce approved readers/writers and use the migration engine
with retained root descriptors, capability checks, and journal checkpoints.

#### Scenario: An approved operation runs

- **GIVEN** readers/writers are quiesced and the live root identity matches the
  approved snapshot
- **WHEN** the migration engine applies one approved operation
- **THEN** it records a value-free journal transition and verifies the result
- **AND** it uses no unsafe pathname fallback or unbounded cleanup

#### Scenario: Live identity drifts

- **GIVEN** the root, descendant, principal, or required platform capability
  differs from the approved plan
- **WHEN** execution reaches the affected boundary
- **THEN** it stops before further mutation
- **AND** it reports recovery status without exposing secret values

### Requirement: Interruption SHALL recover or roll back deterministically

The cutover SHALL use the tested journal recovery/rollback path for faults,
health failures, or withdrawn approval.

#### Scenario: Cutover is interrupted

- **GIVEN** a fault occurs before or after a journal boundary
- **WHEN** the operator invokes recovery under the same approved identity
- **THEN** recovery completes or rolls back idempotently
- **AND** a second invocation produces no additional mutation

#### Scenario: Rollback is required

- **GIVEN** a post-operation health gate fails
- **WHEN** the approved rollback is executed while readers remain quiesced
- **THEN** the recorded snapshot or inverse restores the prior contract
- **AND** unknown files and credentials are not deleted or rewritten

### Requirement: Post-cutover verification SHALL distinguish evidence scopes

The operator SHALL verify provider, filesystem, consumer, deployment, and
scheduler/database outcomes separately before releasing maintenance mode.

#### Scenario: All post-cutover gates pass

- **GIVEN** provider doctor, permissions/links, consumer smoke tests, service
  health, and scheduler/database checks each have owner-attributed evidence
- **WHEN** the cutover report is finalized
- **THEN** only the scopes with direct evidence are marked ready
- **AND** the root snapshot, journal identity, and rollback reference remain
  discoverable

#### Scenario: A post-cutover gate fails

- **GIVEN** any required consumer, deployment, or scheduler check fails or is
  unknown
- **WHEN** the post-cutover report is generated
- **THEN** maintenance mode remains active or rollback is invoked
- **AND** the report does not claim a successful cutover

