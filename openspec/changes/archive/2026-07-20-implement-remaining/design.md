# Design: Implement Remaining Deferred Items

## Overview

This change documents four remaining gaps in the microservices ecosystem and establishes a phased plan to close them. The design focuses on verifiable, independently deployable increments that do not require coordinated releases.

## Context

The ecosystem was standardized in prior changes: all 8 services use `internal/` layout, Dockerfiles follow the canonical template, Makefiles are in place, K8s ports are aligned, and E2E operations have been verified. This change addresses the long tail of deferred items that were identified during audits but not yet implemented.

## Goals

1. Close test coverage gaps to meet the 90/90/80 thresholds across all 8 services.
2. Fix the ArgoCD repoURL placeholder so GitOps sync works end-to-end.
3. Wire Worker Versioning v2 across all 8 Temporal workers.
4. Implement the Kafka retry-topic chain with exponential backoff and DLQ routing.

## Non-Goals

- New service extraction or domain boundary changes.
- Protobuf contract changes or new API endpoints.
- Database schema migrations.
- Observability stack changes (OTel, Prometheus, Grafana are already in place).
- Kubernetes infrastructure changes beyond ArgoCD configuration.
- Circuit breaker pattern (tracked in a separate change).

## Key Decisions

### Decision 1: Phased approach with independent verification

Each phase is independently verifiable and deployable. Phase 1 (test coverage) does not depend on Phase 2 (ArgoCD) or Phase 3 (Worker Versioning v2, Kafka retry). This reduces blast radius and allows incremental progress.

**Rationale**: The gaps span different domains (testing, deployment, runtime). Coupling them increases risk and complicates rollback.

### Decision 2: Worker Versioning v2 rollout is service-by-service

Worker Versioning v2 requires `UseVersioning: true` on the worker AND `UseVersioning: true` on the `startWorkflow` caller. These must be deployed atomically per service. The rollout order will be: notification-service (least traffic), catalog-service, inventory-service, payment-service, shipping-service, customer-service, reporting-service, order-service (most traffic).

**Rationale**: Order-service is the most critical service and should be last to minimize risk. Services with fewer workflows are safer to migrate first.

### Decision 3: Kafka retry-topic chain uses the spec-defined delay schedule

The retry-topic chain will follow the existing spec definition: `<source-topic>.retry.1000`, `.retry.8000`, `.retry.60000`, `.retry.300000`, `.retry.1800000` (1s, 8s, 1min, 5min, 30min delays). After the final attempt, records route to `<source-topic>.dlq`.

**Rationale**: The schedule is already specified in `platform-kafka-harness/spec.md` and represents a reasonable exponential backoff for e-commerce workloads.

### Decision 4: DEFERRED items are explicitly documented with evidence

Worker Versioning v2 and Kafka retry-topic chain are marked DEFERRED in the delta specs with evidence of what exists and what is missing. This prevents future audits from re-discovering the same gaps.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Test coverage improvements introduce flaky tests | Medium | Medium | Use integration tests with Docker Compose; avoid external dependencies in unit tests |
| ArgoCD repoURL fix breaks existing sync | Low | High | Validate against staging before production; use ArgoCD diff preview |
| Worker Versioning v2 causes workflow replay failures | Medium | High | Run replay tests before deploying; deploy to least-critical services first |
| Kafka retry-topic chain creates topic sprawl | Low | Low | Use topic auto-creation with retention policies; document topic naming convention |

## Unresolved Decisions

- **ArgoCD repoURL value**: Depends on the actual Git hosting provider and repository path. Must be confirmed before implementation.
- **Test coverage measurement tool**: `go test -cover` vs `gocov` vs `sonarqube`. Final choice depends on CI pipeline integration.

## Files Modified

### This Change
- `openspec/changes/implement-remaining/proposal.md`
- `openspec/changes/implement-remaining/design.md`
- `openspec/changes/implement-remaining/tasks.md`
- `openspec/changes/implement-remaining/specs/test-coverage-gap-closure/spec.md` (delta)
- `openspec/changes/implement-remaining/specs/operational-readiness/spec.md` (delta)

### Referenced (not modified)
- `openspec/specs/test-coverage-gap-closure/spec.md`
- `openspec/specs/operational-readiness/spec.md`
- `openspec/specs/platform-temporal-versioning/spec.md`
- `openspec/specs/platform-kafka-harness/spec.md`
