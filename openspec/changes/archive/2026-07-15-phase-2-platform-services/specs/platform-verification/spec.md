## ADDED Requirements

### Requirement: Release evidence retention
The release evidence SHALL be retained for at least one year. Pull-request evidence SHALL be retained for at least 30 days.

#### Scenario: Release tag publishes year-long evidence
- **WHEN** a `v*` tag is pushed and `.github/workflows/release-evidence.yml` runs
- **THEN** the workflow uploads `artifacts/verification/${{ github.sha }}` as a GitHub Actions artifact with `retention-days: 365`, confirmed by `grep -E 'retention-days:\s*365' .github/workflows/release-evidence.yml`

#### Scenario: Pull request publishes 30-day evidence
- **WHEN** `.github/workflows/verify.yml` runs on a pull request
- **THEN** the workflow uploads the per-SHA evidence directory as a GitHub Actions artifact with `retention-days: 30`, confirmed by `grep -E 'retention-days:\s*30' .github/workflows/verify.yml`

#### Scenario: Phase-2 platform verification runs across modules in dependency order
- **WHEN** `make verify-release` runs against the multi-module platform after PR-7 (cross-service verification gates) lands
- **THEN** the platform module's `make platform-verify` runs first, each service module's `make verify-pr` runs after the platform passes, and the LGTM overlay is brought up during `test-e2e` so every service's OTel-emitted data lands in Tempo/Mimir/Loki

### Requirement: Phase 2 cross-service verifications are mapped to the verification manifest
The verification manifest SHALL map cross-service verifications PV-100..PV-110 (introduced by Phase 2) and platform verifications PV-200..PV-260 to concrete commands and evidence paths. `verify-traceability` SHALL report zero unmapped scenarios whose capability is in the Phase 2 scope.

#### Scenario: PV-100 covers Order Service captures customer reference snapshot
- **WHEN** the verification manifest is built for the cross-service scope
- **THEN** `PV-100` maps to `make test-e2e::test_cross_service_order_with_customer_snapshot` with evidence `artifacts/verification/local/e2e-customer-snapshot.json`

#### Scenario: PV-200 covers OTel SDK wires up in every service
- **WHEN** the verification manifest is built for the platform scope
- **THEN** `PV-200` maps to `make platform-verify::test_observability_tracer_initialised` with evidence `artifacts/verification/local/observability-tracer.json`

#### Scenario: verify-traceability reports zero unmapped Phase-2 scenarios
- **WHEN** `go run ./cmd/verify-traceability verification/traceability.yaml` runs after the Phase-2 traceability entries are added
- **THEN** the command exits 0 with no `unmapped scenario` lines for any capability whose prefix is `platform-`, `notification-`, `customer-`, `catalog-`, or `reporting-`

### Requirement: OpenSpec validation is part of the release gate
The release gate SHALL include a step that runs `openspec validate --strict --all` and rejects the release if any active change fails validation.

#### Scenario: openspec validate --strict --all is green before release tag
- **WHEN** the release-evidence workflow runs against a `v*` tag
- **THEN** `openspec validate --strict --all` runs and the workflow fails the tag if the command exits non-zero

## ADDED Requirements

### Requirement: Cross-service smoke test verifies end-to-end flow
A Phase-2 release SHALL pass the cross-service smoke test that exercises create-customer → create-product → create-order (Order calls Catalog for price quote, Customer for reference) → process-payment (in-module stub) → notification-fires → reporting-projection-updates.

#### Scenario: Cross-service smoke test publishes evidence under artifacts
- **WHEN** `make test-e2e::test_cross_service_smoke` runs
- **THEN** the test writes `artifacts/verification/local/e2e-cross-service.json` recording the elapsed wall time per stage and the final state of every service's projection

#### Scenario: Cross-service smoke test fails when any service's projection is stale
- **WHEN** any service's projection lags the expected state by more than 5000 ms
- **THEN** the smoke test fails with `cross-service projection lag: <service>=<ms>ms > 5000ms`

### Requirement: Phase 2 traceability manifest is committed before any Phase-2 code lands
The verification manifest SHALL be extended with at least one entry per Phase-2 scenario before any service module is touched. Each entry starts at `status: planned` and flips to `status: implemented` once its target test passes.

#### Scenario: Traceability manifest has PV-100..PV-110 entries
- **WHEN** the manifest is committed alongside the first Phase-2 PR
- **THEN** the manifest contains entries for `PV-100` through `PV-110` covering the cross-service call paths in `internal/application/commands/create_order.go`

#### Scenario: Traceability manifest has PV-200..PV-260 entries
- **WHEN** the manifest is committed alongside the PR-1 (platform module) PR
- **THEN** the manifest contains at least one entry per `### Requirement` in `platform-observability`, `platform-kafka-harness`, `platform-temporal-versioning`, `platform-cache`, and `platform-hexagonal-enforcement`