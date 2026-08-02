# Fix Pre-existing Verification Issues

## Why

Live stack verification revealed 5 pre-existing issues that prevent full test passage:

1. **customer-worker panic**: `RegisterWorkflowWithOptions` receives string constants instead of workflow functions. The workflow implementations (`CustomerPurgeWorkflow`, `CustomerGDPRExportWorker`) were never created.
2. **inventory-service test build failure**: `GenerateReservationID` is called in `activities_test.go` but the function doesn't exist in `activities.go`.
3. **reporting-service architecture test failure**: `TestWorkerVersioningIsConfigured` and `TestDeterministicWorkflowCode` fail because `reportingRepositoryRoot()` can't find a directory named `microservices` in the path (workspace is `~/Developer/go-microservices`).
4. **validation script build failure**: `collectDiagnostics` method is called in `main.go` but never defined on the `runner` struct.
5. **catalog-service coverage**: 77.3% (below 80% gate) — pre-existing gap.

## What Changes

- Implement customer GDPR purge and export workflow functions
- Implement `GenerateReservationID` in inventory-service activities
- Fix reporting-service test path resolution
- Implement `collectDiagnostics` method in validation script
- Add missing unit tests for catalog-service coverage

## Non-Goals

- Full customer workflow implementation (placeholder only — real logic comes later)
- Complete inventory reservation flow (only the ID generator)
- Restructuring the validation script architecture

## Affected Boundaries

- `services/customer-service/internal/application/orchestration/` — new workflow files
- `services/inventory-service/internal/application/orchestration/` — new activity function
- `services/reporting-service/test/architecture/` — path resolution fix
- `scripts/validation/main.go` — missing method
- `services/catalog-service/` — additional tests

## Compatibility

All changes are additive or fix existing broken code. No API contracts change.
