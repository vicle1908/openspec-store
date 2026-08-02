# platform-temporal-versioning Delta Specification

## Purpose

This delta updates the main `platform-temporal-versioning` spec to reflect the temporal-improvements change: Worker Versioning v2 status advances from DEFERRED to IN PROGRESS, and a new workflow replay test requirement is added for all services.

## MODIFIED Requirements

### Requirement: Worker Versioning v2 adoption [IN PROGRESS]

> **Status**: IN PROGRESS. `platformtemporal.DeploymentVersion()` exists in `platform/temporal/deployment.go` and reads `PLATFORM_DEPLOYMENT_VERSION` -> `GIT_SHA` -> `dev`. The `WorkerDeploymentOptions` struct is available. Order-service has partial registration (`BuildID` and `DeploymentSeriesName` set). Customer-service had Worker Versioning v2 wired but removed it after a panic caused by empty `DeploymentVersion()` in local dev. The remaining 6 services do not configure Worker Versioning v2. This change wires all 8 services and fixes the customer-service panic.

Every Temporal worker SHALL register with `UseVersioning: true`, a non-empty `BuildID`, and a service-specific `DeploymentSeriesName`.

#### Scenario: Worker registers with deployment series name (Versioning v2)

- **WHEN** a Temporal worker starts in any service
- **THEN** the worker options include `WorkerDeploymentOptions{ UseVersioning: true, BuildID: <from DeploymentVersion()>, DeploymentSeriesName: "<service-specific>" }`
- **AND** the worker fails fast if `DeploymentVersion()` returns an empty string

#### Scenario: Orchestrator passes UseVersioning on startWorkflow

- **WHEN** any service starts a workflow via `client.ExecuteWorkflow`
- **THEN** the `StartWorkflowOptions` include `UseVersioning: true`

#### Scenario: All 8 workers configure Worker Versioning v2

- **WHEN** the architecture test scans for `WorkerDeploymentOptions{UseVersioning: true, ...}` in `services/<service>/cmd/<service>/`
- **THEN** the test verifies that all 8 services configure `UseVersioning: true` with a non-empty `BuildID` and `DeploymentSeriesName`

#### Scenario: Worker fails fast when DeploymentVersion is empty

- **WHEN** `DeploymentVersion()` returns an empty string (both `PLATFORM_DEPLOYMENT_VERSION` and `GIT_SHA` unset, and the `dev` default is somehow bypassed)
- **THEN** the worker's `runWorker` function panics with `FAIL: DeploymentVersion is empty` before registering any workflows or activities

### Requirement: Workflow replay tests [ADDED]

> **Status**: ADDED. The order-service has `test/compatibility/order_fulfillment_replay_test.go`. The other 7 services (customer-service, notification-service, catalog-service, reporting-service, payment-service, inventory-service, shipping-service) do not have replay tests. This change adds replay tests for all 7 services.

The platform SHALL require every workflow to ship a replay test that runs the workflow against a recorded history. The replay test SHALL live in `test/compatibility/<workflow>_replay_test.go` and SHALL use the Temporal test framework's `test.NewWorkflowEnvironment()` with a `RegisterWorkflowWithOptions` call that references the workflow function. The replay test SHALL fail if the workflow code change would cause a non-deterministic replay.

#### Scenario: Replay test passes against recorded history

- **WHEN** the recorded history is replayed against the new workflow code
- **THEN** the test passes and the workflow produces the same result

#### Scenario: Replay test detects non-deterministic change

- **WHEN** the workflow code introduces a non-deterministic API call (e.g., `time.Now()`, goroutine launch)
- **THEN** the replay test fails with a deterministic-replay error

#### Scenario: All 8 services have replay tests

- **WHEN** `make verify-pr` runs for any service that defines a Temporal workflow
- **THEN** the service contains at least one `*_replay_test.go` file in `test/compatibility/`
- **AND** the replay test passes against the current workflow code
