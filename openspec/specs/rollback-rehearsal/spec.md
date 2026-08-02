# rollback-rehearsal Specification

## Purpose

Provides a rollback rehearsal script (`scripts/rehearse-rollback.sh`) that verifies a release can be rolled back safely, plus a runbook (`docs/runbooks/rollback.md`) documenting the zero-downtime rollback procedure for order-service, including database migration rollback and Docker image rollback.

## Requirements

> **Status**: IMPLEMENTED. scripts/rehearse-rollback.sh with 5-step rehearsal and docs/runbooks/rollback.md runbook exist.

### Requirement: Rollback rehearsal script exists at scripts/rehearse-rollback.sh

The project SHALL provide `scripts/rehearse-rollback.sh` that executes a 5-step rollback rehearsal: check current state, simulate rollback, verify health checks, run smoke tests, and roll forward.

#### Scenario: Rollback rehearsal completes successfully
- **WHEN** an operator runs `scripts/rehearse-rollback.sh` against a healthy local stack
- **THEN** the script exits with code 0 and prints a success message for each step

#### Scenario: Rollback rehearsal detects health check failure
- **WHEN** the rollback simulation produces a service that fails health checks
- **THEN** the script exits with code 1 and prints which service failed its health check

### Requirement: Rollback rehearsal is idempotent

The rollback rehearsal script MUST be safe to run multiple times. It MUST always leave the stack in the "current version" state by rolling forward at the end.

#### Scenario: Rollback rehearsal run twice in succession
- **WHEN** an operator runs `scripts/rehearse-rollback.sh` twice without manual intervention
- **THEN** both runs complete with exit code 0 and the stack is in the same state after each run

### Requirement: Rollback rehearsal is observable

Each step of the rehearsal MUST print a clear status message indicating what is being tested and whether it passed.

#### Scenario: Operator observes rehearsal progress
- **WHEN** an operator runs `scripts/rehearse-rollback.sh`
- **THEN** the script prints numbered status messages for each of the 5 steps

### Requirement: Rehearsal driver exists and is executable

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
