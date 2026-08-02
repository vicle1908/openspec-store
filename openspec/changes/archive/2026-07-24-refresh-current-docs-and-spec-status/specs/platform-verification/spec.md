## MODIFIED Requirements

### Requirement: Cross-service smoke test verifies end-to-end flow

> **Status**: IMPLEMENTED. Cross-service smoke test exists; exercises create-customer through reporting-projection.

A Phase-2 release SHALL pass the canonical cross-service smoke test that
exercises create-customer → create-product → create-order (Order calls Catalog
for price quote, Customer for reference) → process-payment (in-module stub) →
notification-fires → reporting-projection-updates. The authoritative local
entry point is `make dev-smoke`; `make dev-evidence` SHALL retain the exact
timestamped smoke report and project-bound evidence manifest.

#### Scenario: Cross-service smoke test publishes evidence under artifacts
- **WHEN** `make dev-smoke` runs successfully inside the isolated Compose project
- **THEN** it writes a passing `artifacts/verification/local/cross-service-smoke-<timestamp>.json` report containing stage results and the final projection state

#### Scenario: Compose evidence binds the exact smoke report
- **WHEN** `make dev-evidence` runs with the exact passing smoke report
- **THEN** it writes a `microservices.compose-acceptance/v1` manifest that hashes the smoke report, worker readiness, Compose state, resolved model, and image inventory

#### Scenario: Cross-service smoke test fails when any service's projection is stale
- **WHEN** any service's projection lags the expected state by more than 5000 ms
- **THEN** the smoke test fails with `cross-service projection lag: <service>=<ms>ms > 5000ms`
