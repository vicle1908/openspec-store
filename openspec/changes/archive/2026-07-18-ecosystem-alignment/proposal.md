# Proposal: Ecosystem Alignment

## Problem

The microservices ecosystem has been standardized across 8 services with `internal/` layout, passing tests, Dockerfiles, Makefiles, and K8s port alignment. However, five categories of gaps remain that prevent the platform from reaching full operational maturity:

1. **ArgoCD repoURL is a placeholder** -- The ArgoCD Application manifests reference a placeholder repository URL instead of the actual Git repository. GitOps sync will fail until this is resolved.
2. **Test coverage gaps in non-order services** -- The target thresholds are 90% unit / 90% integration / 80% architecture-test coverage. Only order-service meets these targets; the remaining 7 services fall below the thresholds.
3. **Worker Versioning v2 is not wired** -- The spec requires every Temporal worker to register with `UseVersioning: true`, a `BuildID`, and a `DeploymentSeriesName`. Only order-service has partial registration; the other 7 services do not configure it.
4. **Kafka retry-topic chain is not implemented** -- The platform-kafka-harness spec defines a retry-topic chain with exponential backoff, DLQ routing, and `RetryConsumer`. The consumer publishes to retry topics on `RetryableError` but the full chain including delay-before-republish and DLQ routing is not wired.
5. **Circuit breaker pattern is deferred** -- No implementation exists for outbound HTTP/gRPC circuit breaker middleware.

## Solution

This change creates a phased plan to close these gaps. Each phase is independently deployable and verifiable:

- **Phase 1 (Critical)**: Close test coverage gaps across all 8 services.
- **Phase 2 (High)**: Fix ArgoCD repoURL and wire Worker Versioning v2 across all Temporal workers.
- **Phase 3 (Medium)**: Implement Kafka retry-topic chain and circuit breaker pattern.

## Scope

### Modified Capabilities
- `operational-readiness` -- Add ArgoCD repoURL requirement; update test coverage thresholds
- `platform-temporal-versioning` -- Mark Worker Versioning v2 as DEFERRED with evidence
- `platform-kafka-harness` -- Mark retry-topic chain as DEFERRED with evidence
- `circuit-breaker` -- Referenced but not modified in this change (tracked separately)

### New Capabilities
- None -- this change closes existing gaps, not introduces new capabilities

## Impact

- **Service boundaries**: No new service boundaries. All changes are within existing services or platform libraries.
- **Contracts**: No protobuf or REST contract changes.
- **Data ownership**: No schema migrations. Test coverage and deployment configuration only.
- **Cross-service dependencies**: Worker Versioning v2 requires coordinated rollout across all 8 services.
- **Rollback**: Test coverage changes are additive (new tests, no behavior changes). ArgoCD repoURL is a configuration fix. Worker Versioning v2 can be rolled back by setting `UseVersioning: false`.
- **Compatibility**: All changes are backward-compatible. No breaking changes to APIs, data formats, or deployment contracts.

## Status Definitions
- **IMPLEMENTED**: Code exists and matches spec requirement
- **PARTIAL**: Some code exists but does not fully meet spec
- **DEFERRED**: No code exists yet, planned for future work
