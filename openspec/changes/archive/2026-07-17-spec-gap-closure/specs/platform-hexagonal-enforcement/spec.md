# platform-hexagonal-enforcement Delta Specification

## Purpose

This delta updates the main `platform-hexagonal-enforcement` spec to reflect the actual implementation status discovered during the spec-gap-closure audit. One requirement has modified status, and a new scenario is added for architecture test completeness.

## MODIFIED Requirements

### Requirement: Architecture test coverage [PARTIAL]

> **Status**: PARTIAL. Most services include a `layering_test.go` in `test/architecture/` that covers a subset of the 12 required test categories. The full matrix of 12 tests (`TestDomainDoesNotImportAdapters`, `TestApplicationDoesNotImportAdapters`, `TestAdaptersDoNotImportEachOther`, `TestPortsDoNotImportAdapters`, `TestSoleWriterRule`, `TestPortsAreInterfaces`, `TestAdapterImplementsExactlyOnePort`, `TestDomainInvariantsAreEnforced`, `TestBuildTagIsolation`, `TestCacheKeyspaceDeclaration`, `TestWorkerVersioningIsConfigured`, `TestDeterministicWorkflowCode`) is not present in every service. Several services have only 4-6 of the 12 required tests, and the `TestDomainInvariantsAreEnforced`, `TestCacheKeyspaceDeclaration`, and `TestWorkerVersioningIsConfigured` tests are missing from most services.

Every service SHALL include the following architecture tests in `test/architecture/` (each is a Go test that exits non-zero on violation):

| Test | Purpose |
|---|---|
| `TestDomainDoesNotImportAdapters` | Domain layer is pure |
| `TestApplicationDoesNotImportAdapters` | Application layer is pure |
| `TestAdaptersDoNotImportEachOther` | Cross-adapter coupling is forbidden |
| `TestPortsDoNotImportAdapters` | Ports do not depend on adapters |
| `TestSoleWriterRule` | Each service owns its schema |
| `TestPortsAreInterfaces` | Cross-boundary types are interfaces |
| `TestAdapterImplementsExactlyOnePort` | Adapters are focused |
| `TestDomainInvariantsAreEnforced` | Domain invariants return typed errors |
| `TestBuildTagIsolation` | Optional adapters are build-tag-gated |
| `TestCacheKeyspaceDeclaration` (when cache is used) | All cache keys follow the canonical pattern |
| `TestWorkerVersioningIsConfigured` (when Temporal is used) | Worker Versioning v2 is configured |
| `TestDeterministicWorkflowCode` (when Temporal is used) | Workflow code uses only deterministic APIs |

The architecture tests SHALL run as part of `make verify-pr` and SHALL fail the build on any violation. The architecture tests SHALL be invoked before `make test-unit` so a layering violation fails fast.

#### Scenario: Architecture test fails the PR gate

- **WHEN** a service introduces a layering violation
- **THEN** `make verify-pr` exits non-zero at the architecture-test step

#### Scenario: Architecture tests run before unit tests

- **WHEN** `make verify-pr` runs
- **THEN** the architecture tests complete before the unit tests start

#### Scenario: Architecture test completeness check

- **WHEN** the architecture test suite runs for any service
- **THEN** every test in the 12-test matrix above is present in `test/architecture/` for that service (or explicitly documented as not applicable with a reason)
- **AND** the CI pipeline verifies that no required test is missing by scanning `test/architecture/*_test.go` for the expected test function names
- **AND** a missing test function causes the CI step to fail with a message identifying which test is absent and in which service

#### Scenario: Temporal-using services include temporal-specific tests

- **WHEN** a service imports `platform/temporal` or registers Temporal workers
- **THEN** `test/architecture/` includes `TestWorkerVersioningIsConfigured` and `TestDeterministicWorkflowCode`
- **AND** the absence of either test fails the CI gate
