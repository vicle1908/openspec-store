# platform-temporal-versioning Delta Spec

> **Change**: ecosystem-alignment
> **Base**: openspec/specs/platform-temporal-versioning/spec.md
> **Date**: 2026-07-18

## Purpose

This delta documents the DEFERRED status of Worker Versioning v2 adoption across all 8 services.

---

## MODIFIED Requirements

### Requirement: Worker Versioning v2 adoption is required for all eight workers

> **Status**: DEFERRED. `platformtemporal.DeploymentVersion()` exists in `platform/temporal/deployment.go` and the `WorkerDeploymentOptions` struct is available. However, full Worker Versioning v2 adoption is not wired across all services. Only order-service has partial registration; the other seven services do not configure Worker Versioning v2.

Every Temporal worker SHALL register with `UseVersioning: true`, a non-empty `BuildID`, and a service-specific `DeploymentSeriesName`. The `BuildID` SHALL be supplied by `platformtemporal.DeploymentVersion()`. The worker SHALL fail fast with `FAIL: DeploymentVersion is empty` if no source produces a value.

#### Scenario: Worker registers with deployment series name (Versioning v2)

- **WHEN** a Temporal worker starts in any of the 8 services
- **THEN** the worker options include `WorkerDeploymentOptions{ UseVersioning: true, BuildID: <from DeploymentVersion()>, DeploymentSeriesName: "<service-specific>" }`
- **AND** the worker fails fast if `DeploymentVersion()` returns an empty string

#### Scenario: Orchestrator passes UseVersioning on startWorkflow

- **WHEN** any service starts a workflow via `client.ExecuteWorkflow`
- **THEN** the `StartWorkflowOptions` include `UseVersioning: true`

#### Scenario: Worker Versioning v2 is wired in all 8 services

- **WHEN** the architecture test scans for `WorkerDeploymentOptions{UseVersioning: true, ...}` in all service worker initialization
- **THEN** the test verifies that all 8 services configure `UseVersioning: true` with a non-empty `BuildID` and `DeploymentSeriesName`
