## ADDED Requirements

### Requirement: Rollback rehearsal driver exists and is executable

The repository SHALL publish `scripts/rehearse-rollback.sh` and `make test-rollback-rehearsal` so a candidate build can be exercised against a pinned prior-release fixture. The driver SHALL refuse to start when the pinned prior fixture is missing and SHALL exit with a deterministic status (`passed`, `failed`, or `planned`).

#### Scenario: Rehearsal runs against the pinned prior fixture
- **WHEN** a developer or CI run executes `make test-rollback-rehearsal` and `proto-baseline/v0.1.0/`, prior migration fixture, and prior Temporal history fixture all exist
- **THEN** the driver boots the prior image plus the prior-schema database, replays retained Temporal histories against the candidate worker, and exits with status `passed` if no business-effect loss is detected

#### Scenario: Rehearsal detects lost business effects
- **WHEN** the candidate worker cannot reconcile an in-flight Temporal history against the prior schema
- **THEN** the driver exits with status `failed`, the gap is recorded with the failing history id and stack trace, and the rehearsal target blocks the release tag

#### Scenario: No prior fixture is available
- **WHEN** no previous-release fixture exists for the candidate build
- **THEN** the driver exits with status `planned`, the gap is recorded in the evidence manifest with an owner and expiry date, and the rehearsal target does NOT falsely report `passed`

### Requirement: Rollback runbook documents the operational procedure

The repository SHALL publish `docs/runbooks/rollback.md` describing the operational rollback procedure for production deployments. The runbook MUST reference the rehearsal driver, MUST identify the expand/contract migration contract, and MUST be reachable from `docs/runbooks/README.md`.

#### Scenario: Operator follows the rollback runbook during an incident
- **WHEN** an operator opens `docs/runbooks/rollback.md` during a production rollback incident
- **THEN** the runbook identifies the prior image tag, the prior-schema database upgrade path, the workflow replay expectation, and the steps required to roll back to the prior release without data loss

#### Scenario: Runbook diverges from the rehearsal driver
- **WHEN** the rehearsal driver's executable commands differ from the documented runbook steps
- **THEN** the make `verify-traceability` validator reports the divergence as a forbidden skip because the runbook is the source of truth for the verification ID