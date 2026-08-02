# platform-temporal-versioning Delta Specification

## Purpose

This delta updates the main `platform-temporal-versioning` spec to reflect the actual implementation status discovered during the spec-gap-closure audit. Two requirements have modified status annotations.

## MODIFIED Requirements

### Requirement: Worker Versioning v2 adoption [DEFERRED]

> **Status**: DEFERRED. The platform provides `platformtemporal.DeploymentVersion()` in `platform/temporal/deployment.go` and the `WorkerDeploymentOptions` struct is available. However, full Worker Versioning v2 adoption — where every worker registers with `UseVersioning: true`, a `BuildID` from `DeploymentVersion()`, and a service-specific `DeploymentSeriesName`, and the orchestrator passes `UseVersioning: true` on `startWorkflow` calls — is not wired across all services. Only the order-service has partial registration; the other seven services do not yet configure Worker Versioning v2.

Every Temporal worker SHALL register with `UseVersioning: true`, a non-empty `BuildID`, and a service-specific `DeploymentSeriesName`.

#### Scenario: Worker registers with deployment series name (Versioning v2)

- **WHEN** a Temporal worker starts in any service
- **THEN** the worker options include `WorkerDeploymentOptions{ UseVersioning: true, BuildID: <from DeploymentVersion()>, DeploymentSeriesName: "<service-specific>" }`
- **AND** the worker fails fast if `DeploymentVersion()` returns an empty string

#### Scenario: Orchestrator passes UseVersioning on startWorkflow

- **WHEN** any service starts a workflow via `client.ExecuteWorkflow`
- **THEN** the `StartWorkflowOptions` include `UseVersioning: true`

### Requirement: Deterministic workflow code [PARTIAL]

> **Status**: PARTIAL. The `platform/workflows/workflowcheck/` package provides a `go/analysis` compatible checker and a CLI in `platform/cmd/workflowcheck/main.go` that detects `time.Now()`, `time.Sleep()`, `math/rand`, goroutines, channels, and `sync.Mutex`. However, the checker is not fully integrated into the CI pipeline for all services. Some services run `workflowcheck` as part of their build, while others rely only on replay tests for determinism verification. The allowlist in `.workflowcheck.yaml` is not consistently configured across all services.

Workflow code SHALL be deterministic: it MUST NOT call `time.Now`, MUST NOT launch goroutines, MUST NOT use `math/rand`, and MUST NOT perform I/O. The platform SHALL provide a `workflowcheck` static analysis test that fails the build when any of these appear in a `workflow.go` file under `application/orchestration/`.

#### Scenario: workflowcheck rejects time.Now and goroutines in workflow code

- **WHEN** a `workflow.go` file under `application/orchestration/` calls `time.Now()` or launches a goroutine
- **THEN** the `workflowcheck` test fails the build with the offending file and line number

#### Scenario: workflowcheck is integrated in CI for all Temporal-using services

- **WHEN** `make verify-pr` runs for any service that imports Temporal workflow code
- **THEN** the `workflowcheck` linter runs as part of the build
- **AND** the build fails if `workflowcheck` detects any non-deterministic API call in workflow files
- **AND** the `.workflowcheck.yaml` allowlist is loaded from the service's root directory (or the platform root if not present)

#### Scenario: workflowcheck allowlist is consistent across services

- **WHEN** a new service with Temporal workflows is added
- **THEN** the service includes a `.workflowcheck.yaml` that either mirrors the platform allowlist or documents service-specific exceptions
- **AND** the CI step verifies the allowlist file exists
