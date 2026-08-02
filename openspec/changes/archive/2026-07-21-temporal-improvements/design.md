# Design: Temporal Improvements

## Context

The microservices platform runs 8 services with Temporal workers: order-service, customer-service, notification-service, catalog-service, reporting-service, payment-service, inventory-service, and shipping-service. The platform provides shared Temporal infrastructure in `platform/temporal/` including `DeploymentVersion()`, `NewValidatedActivityOptions`, `NewSaga`, `OperationID`, and `workflowcheck`.

Current state from the architecture evaluation:

- **Worker Versioning v2**: `platformtemporal.DeploymentVersion()` exists in `platform/temporal/deployment.go` and reads `PLATFORM_DEPLOYMENT_VERSION` -> `GIT_SHA` -> `dev` in that order. The `WorkerDeploymentOptions` struct is available. However, only order-service has partial registration (`BuildID` and `DeploymentSeriesName` set, but `UseVersioning: true` not passed on `startWorkflow` calls). The other 7 services do not configure Worker Versioning v2 at all. Customer-service had it wired but removed it after a panic caused by `DeploymentVersion()` returning empty in local dev.
- **Workflow replay tests**: Only `services/order-service/test/compatibility/order_fulfillment_replay_test.go` exists. The other 7 services' workflows have no replay tests.
- **Circuit breaker**: `sony/gobreaker` is a dependency in `services/order-service/internal/adapters/temporal/clients/`. The HTTP clients (`payment_client.go`, `inventory_client.go`, `shipping_client.go`) create gobreaker instances, but the activity code in `activities.go` does not consistently wrap `ErrPeerUnavailable` as `NonRetryableApplicationError`. No integration test exercises the open-circuit -> compensation path.

## Goals

1. Wire Worker Versioning v2 across all 8 Temporal workers with atomic per-service deployment.
2. Fix the customer-service panic by ensuring `DeploymentVersion()` always returns a non-empty string (the `dev` default handles local dev).
3. Add workflow replay tests for all 7 services that lack them.
4. Complete the circuit breaker integration in order-service activities so that an open circuit triggers the workflow compensation path.
5. Add an architecture test that enforces Worker Versioning v2 across all services.

## Non-Goals

- New service extraction or domain boundary changes.
- Protobuf contract changes or new API endpoints.
- Database schema migrations.
- Kafka retry-topic chain implementation (tracked separately).
- Observability stack changes.
- Changing the Temporal namespace strategy (one namespace per environment).

## Key Decisions

### Decision 1: Worker Versioning v2 rollout is service-by-service

Each service's worker and caller must be deployed atomically. The rollout order is: notification-service (least traffic, fewest workflows), catalog-service, inventory-service, payment-service, shipping-service, customer-service, reporting-service, order-service (most critical). This minimizes blast radius.

**Rationale**: Order-service is the most critical and should be last. Services with fewer workflows are safer to migrate first. Each service can be verified independently before proceeding to the next.

**Alternatives considered**:
- Big-bang rollout (all 8 at once): Rejected because a failure in any service would require rolling back all 8 simultaneously.
- Order-service first: Rejected because it carries the highest risk; best to build confidence on lower-traffic services.

### Decision 2: DeploymentVersion() always returns non-empty string

The customer-service panic occurred because `DeploymentVersion()` returned empty when neither `PLATFORM_DEPLOYMENT_VERSION` nor `GIT_SHA` was set. The fix is to ensure the function's fallback chain always terminates with `"dev"` (which it already does in `platform/temporal/deployment.go`). The additional safety measure is a `failFast` check in each worker's `runWorker` function that panics with `FAIL: DeploymentVersion is empty` if the value is somehow empty.

**Rationale**: The `"dev"` default already exists in the code. The panic was caused by a different code path (possibly a direct call to the underlying env lookup rather than the wrapper). Adding a fail-fast guard at the worker level is defense-in-depth.

**Alternatives considered**:
- Remove the fail-fast guard and let empty BuildID through: Rejected because it would silently disable versioning, defeating the purpose.
- Change the env var lookup to never return empty: Rejected because it is already implemented this way; the root cause was a different call path.

### Decision 3: Replay tests use the Temporal test framework

Each replay test will use `tests.NewTestWorkflowEnvironment()` (or `test.NewWorkflowEnvironment()` depending on SDK version) with `RegisterWorkflowWithOptions`. The test will record a successful workflow execution history and replay it against the current workflow code.

**Rationale**: This is the standard Temporal replay testing pattern and is already validated by the order-service's existing replay test.

**Alternatives considered**:
- Static analysis only (workflowcheck): Rejected because workflowcheck catches non-deterministic API calls but does not verify that the workflow's control flow matches a recorded history.
- Manual code review: Rejected because it does not scale and cannot catch subtle non-determinism.

### Decision 4: Circuit breaker integration uses NonRetryableApplicationError

When the circuit breaker is open, the HTTP client returns `clients.ErrPeerUnavailable`. The activity MUST wrap this as `temporal.NewNonRetryableApplicationError("peer_unavailable", "PEER_UNAVAILABLE", err)`. This prevents Temporal from retrying the activity (which would fail immediately since the circuit is still open) and triggers the workflow's compensation path.

**Rationale**: Retrying an activity when the downstream is unreachable wastes retry budget and delays compensation. The workflow's saga compensation is designed to handle this case.

**Alternatives considered**:
- RetryableApplicationError with backoff: Rejected because the circuit breaker's recovery timeout (30s) is longer than Temporal's default retry interval, so retries would all fail.
- Custom error type: Rejected because `NonRetryableApplicationError` is the SDK-native mechanism and integrates with Temporal's retry policy automatically.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Worker Versioning v2 causes workflow replay failures during migration | Medium | High | Run replay tests before deploying each service; deploy to least-critical services first; `UseVersioning: false` is a one-line rollback |
| Customer-service panic recurs after re-applying Worker Versioning v2 | Low | High | Add fail-fast guard that checks `DeploymentVersion()` is non-empty before worker starts; test in local dev without env vars |
| Replay tests are brittle and break on unrelated workflow changes | Medium | Low | Use recorded histories from stable releases; update recordings as part of workflow evolution tasks |
| Circuit breaker integration test is flaky due to timing | Low | Medium | Use deterministic mock HTTP server; avoid real network calls in tests |
| Architecture test produces false positives for services without Temporal workers | Low | Low | Guard the test with a build tag or source-file presence check |

## Unresolved Decisions

- **Replay test history recording**: Whether to record histories from integration tests (automated) or from staging deployments (manual). Automated recording is preferred but requires a test helper that captures Temporal history.
- **Circuit breaker configuration values**: The order-service's existing gobreaker settings (5 failures, 30s recovery) are reasonable defaults but may need tuning based on production traffic patterns. This is an operational concern, not a design decision.

## Files Modified

### This Change
- `openspec/changes/temporal-improvements/proposal.md`
- `openspec/changes/temporal-improvements/design.md`
- `openspec/changes/temporal-improvements/tasks.md`
- `openspec/changes/temporal-improvements/specs/platform-temporal-versioning/spec.md` (delta)
- `openspec/changes/temporal-improvements/specs/order-temporal-workflow/spec.md` (delta)

### Referenced (not modified)
- `openspec/specs/platform-temporal-versioning/spec.md`
- `openspec/specs/order-temporal-workflow/spec.md`
- `openspec/specs/circuit-breaker/spec.md`
- `platform/temporal/deployment.go`
- `platform/temporal/activity_options.go`
- `services/order-service/internal/adapters/temporal/activities.go`
- `services/order-service/internal/adapters/temporal/clients/`
