# Proposal: Temporal Improvements

## Why

The Temporal architecture evaluation (2026-07-18) identified four systemic gaps that block production readiness for durable orchestration across the platform:

1. **Worker Versioning v2 not fully configured** -- Only 3 of 8 Temporal-using services have partial Worker Versioning v2 registration. The remaining 5 services (customer-service, notification-service, catalog-service, reporting-service, and one of the extracted services) do not configure `UseVersioning: true`, `BuildID`, or `DeploymentSeriesName`. Without Worker Versioning v2, in-flight workflows cannot be safely routed to compatible worker builds during rolling deployments.

2. **Customer-service Worker Versioning removed due to panic** -- The customer-service originally had Worker Versioning v2 wired, but it was removed after a runtime panic during startup. The root cause (empty `DeploymentVersion()` when `PLATFORM_DEPLOYMENT_VERSION` and `GIT_SHA` are unset in local development) was identified but the fix was not re-applied.

3. **No workflow replay tests** -- The platform-temporal-versioning spec requires every workflow to ship a replay test. Only the order-service has `test/compatibility/order_fulfillment_replay_test.go`. The other 7 services' workflows (notification dispatch, customer purge/export, catalog price rollback, reporting admin, payment capture, inventory reservation, shipping dispatch) have no replay tests. This means workflow code changes could introduce non-determinism undetected.

4. **No circuit breaker pattern for HTTP calls** -- The order-service activities call payment-service, inventory-service, and shipping-service over HTTP. The `sony/gobreaker` dependency exists in the HTTP clients, but the open-circuit to activity-failure to workflow-compensation chain is not fully wired. The activity body does not treat `ErrPeerUnavailable` as a `NonRetryableApplicationError` in all code paths, and no integration test exercises the compensation path when the circuit is open.

## What Changes

- Complete Worker Versioning v2 registration for all 8 Temporal-using services, including the fix for the customer-service panic (empty `DeploymentVersion()` fallback).
- Add workflow replay tests for the 7 services that lack them.
- Wire the circuit breaker's `ErrPeerUnavailable` to `NonRetryableApplicationError` in all order-service activity code paths and add an integration test for the compensation path.
- Add an architecture test that verifies all 8 workers configure Worker Versioning v2.

## Capabilities

### Modified Capabilities

- `platform-temporal-versioning`: Update Worker Versioning v2 status from DEFERRED to IN PROGRESS. Add workflow replay test requirement for all services.
- `order-temporal-workflow`: Update circuit breaker status from DEFERRED to IN PROGRESS. Add activity timeout enforcement requirement for all activities.

### New Capabilities

- None -- this change closes existing gaps, not introduces new capabilities.

## Impact

- **Service boundaries**: No new service boundaries. Worker Versioning v2 changes are per-service worker configuration only.
- **Contracts**: No protobuf or REST contract changes.
- **Data ownership**: No schema migrations. Temporal workflow code and worker configuration changes only.
- **Cross-service dependencies**: Worker Versioning v2 requires coordinated rollout -- all workers in a service must be deployed atomically (worker + caller). However, services can be migrated independently of each other.
- **Rollback**: Worker Versioning v2 can be rolled back by setting `UseVersioning: false` and redeploying. Circuit breaker wiring is additive (new error handling paths, no behavior change on the happy path). Replay tests are additive (new test files, no production code change).
- **Compatibility**: All changes are backward-compatible. No breaking changes to APIs, data formats, or deployment contracts.

## Status Definitions

- **IMPLEMENTED**: Code exists and matches spec requirement
- **PARTIAL**: Some code exists but does not fully meet spec
- **DEFERRED**: No code exists yet, planned for future work
- **IN PROGRESS**: Implementation has started but is not yet complete
