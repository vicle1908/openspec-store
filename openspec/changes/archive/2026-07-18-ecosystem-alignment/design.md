# Design: Ecosystem Alignment

## Overview

This change documents five remaining gaps in the microservices ecosystem and establishes a phased plan to close them. The design focuses on verifiable, independently deployable increments that do not require coordinated releases.

## Context

The ecosystem was standardized in prior changes: all 8 services use `internal/` layout, Dockerfiles follow the canonical template, Makefiles are in place, K8s ports are aligned, and E2E operations have been verified. This change addresses the long tail of gaps that were identified during the audit but deferred.

## Goals

1. Close test coverage gaps to meet the 90/90/80 thresholds across all 8 services.
2. Fix the ArgoCD repoURL placeholder so GitOps sync works end-to-end.
3. Wire Worker Versioning v2 across all 8 Temporal workers.
4. Implement the Kafka retry-topic chain with exponential backoff and DLQ routing.
5. Establish a circuit breaker pattern for outbound HTTP/gRPC calls.

## Non-Goals

- New service extraction or domain boundary changes.
- Protobuf contract changes or new API endpoints.
- Database schema migrations.
- Observability stack changes (OTel, Prometheus, Grafana are already in place).
- Kubernetes infrastructure changes beyond ArgoCD configuration.

## Key Decisions

### Decision 1: Phased approach with independent verification

Each phase is independently verifiable and deployable. Phase 1 (test coverage) does not depend on Phase 2 (ArgoCD/Worker Versioning) or Phase 3 (Kafka/circuit breaker). This reduces blast radius and allows incremental progress.

**Rationale**: The gaps span different domains (testing, deployment, runtime). Coupling them increases risk and complicates rollback.

### Decision 2: Worker Versioning v2 rollout is service-by-service

Worker Versioning v2 requires `UseVersioning: true` on the worker AND `UseVersioning: true` on the `startWorkflow` caller. These must be deployed atomically per service. The rollout order will be: notification-service (least traffic), catalog-service, inventory-service, payment-service, shipping-service, customer-service, reporting-service, order-service (most traffic).

**Rationale**: Order-service is the most critical service and should be last to minimize risk. Services with fewer workflows are safer to migrate first.

### Decision 3: Kafka retry-topic chain uses the spec-defined delay schedule

The retry-topic chain will follow the existing spec definition: `<source-topic>.retry.1000`, `.retry.8000`, `.retry.60000`, `.retry.300000`, `.retry.1800000` (1s, 8s, 1min, 5min, 30min delays). After the final attempt, records route to `<source-topic>.dlq`.

**Rationale**: The schedule is already specified in `platform-kafka-harness/spec.md` and represents a reasonable exponential backoff for e-commerce workloads.

### Decision 4: Circuit breaker pattern uses a well-known library

The circuit breaker will use the `sony/gobreaker` library (or equivalent) wrapped in platform middleware. The pattern will be implemented as HTTP middleware and gRPC interceptor, not as a per-call wrapper.

**Rationale**: Using a well-tested library avoids reinventing state machine logic. Middleware/interceptor pattern ensures consistent application across all outbound calls.

### Decision 5: DEFERRED items are explicitly documented with evidence

Worker Versioning v2 and Kafka retry-topic chain are marked DEFERRED in the delta specs with evidence of what exists and what is missing. This prevents future audits from re-discovering the same gaps.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Test coverage improvements introduce flaky tests | Medium | Medium | Use integration tests with Docker Compose; avoid external dependencies in unit tests |
| ArgoCD repoURL fix breaks existing sync | Low | High | Validate against staging before production; use ArgoCD diff preview |
| Worker Versioning v2 causes workflow replay failures | Medium | High | Run replay tests before deploying; deploy to least-critical services first |
| Kafka retry-topic chain creates topic sprawl | Low | Low | Use topic auto-creation with retention policies; document topic naming convention |
| Circuit breaker false OPEN during deploy | Medium | Low | Use conservative thresholds (5 failures, 30s recovery); monitor during rollout |

## Unresolved Decisions

- **Circuit breaker library**: `sony/gobreaker` vs `afex/circe` vs custom implementation. Final choice depends on Go module compatibility and maintenance status at time of implementation.
- **Test coverage measurement tool**: `go test -cover` vs `gocov` vs `sonarqube`. Final choice depends on CI pipeline integration.
- **ArgoCD repoURL value**: Depends on the actual Git hosting provider and repository path. Must be confirmed before implementation.

## Files Modified

### This Change
- `openspec/changes/ecosystem-alignment/proposal.md`
- `openspec/changes/ecosystem-alignment/design.md`
- `openspec/changes/ecosystem-alignment/tasks.md`
- `openspec/changes/ecosystem-alignment/specs/operational-readiness/spec.md` (delta)
- `openspec/changes/ecosystem-alignment/specs/platform-temporal-versioning/spec.md` (delta)
- `openspec/changes/ecosystem-alignment/specs/platform-kafka-harness/spec.md` (delta)

### Referenced (not modified)
- `openspec/specs/operational-readiness/spec.md`
- `openspec/specs/platform-temporal-versioning/spec.md`
- `openspec/specs/platform-kafka-harness/spec.md`
- `openspec/specs/circuit-breaker/spec.md`
