# Proposal: Implement Remaining Deferred Items

## Problem

The microservices ecosystem has been standardized across 8 services with `internal/` layout, passing tests, Dockerfiles, Makefiles, K8s port alignment, and E2E operations verified. However, four categories of deferred items remain that prevent the platform from reaching full operational maturity:

1. **Test coverage gaps in non-order services** -- The target thresholds are 90% unit / 90% integration / 80% architecture-test coverage. Only order-service meets these targets; the remaining 7 services fall below the thresholds.
2. **ArgoCD repoURL is a placeholder** -- The ArgoCD Application manifests reference a placeholder repository URL instead of the actual Git repository. GitOps sync will fail until this is resolved.
3. **Worker Versioning v2 is not wired** -- The spec requires every Temporal worker to register with `UseVersioning: true`, a `BuildID`, and a `DeploymentSeriesName`. Only order-service has partial registration; the other 7 services do not configure it.
4. **Kafka retry-topic chain is not implemented** -- The platform-kafka-harness spec defines a retry-topic chain with exponential backoff, DLQ routing, and `RetryConsumer`. The consumer publishes to retry topics on `RetryableError` but the full chain including delay-before-republish and DLQ routing is not wired.

## Solution

This change creates a phased plan to close these gaps. Each phase is independently deployable and verifiable:

- **Phase 1 (Critical)**: Close test coverage gaps across all 8 services to meet 90/90/80 thresholds.
- **Phase 2 (High)**: Fix ArgoCD repoURL so GitOps sync works end-to-end.
- **Phase 3 (Medium)**: Wire Worker Versioning v2 across all 8 Temporal workers and implement the Kafka retry-topic chain.

## Scope

### Modified Capabilities
- `test-coverage-gap-closure` -- Update status annotations to reflect current test counts and mark remaining gaps
- `operational-readiness` -- Add ArgoCD repoURL requirement status; update test coverage threshold enforcement status

### New Capabilities
- None -- this change closes existing deferred gaps, not introduces new capabilities

## Impact

- **Service boundaries**: No new service boundaries. All changes are within existing services or platform libraries.
- **Contracts**: No protobuf or REST contract changes.
- **Data ownership**: No schema migrations. Test coverage and deployment configuration only.
- **Cross-service dependencies**: Worker Versioning v2 requires coordinated rollout across all 8 services.
- **Rollback**: Test coverage changes are additive (new tests, no behavior changes). ArgoCD repoURL is a configuration fix. Worker Versioning v2 can be rolled back by setting `UseVersioning: false`.
- **Compatibility**: All changes are backward-compatible. No breaking changes to APIs, data formats, or deployment contracts.
