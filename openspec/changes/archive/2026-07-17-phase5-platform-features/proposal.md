# Phase 5: Platform Features

**Status:** Proposed
**Date:** 2026-07-17
**Owner:** engineering

## Summary

Phase 5 addresses platform-level feature gaps identified in the Phase 2 audit. These are cross-cutting concerns that improve reliability, resilience, and testing quality across all services.

## Problem Statement

The current architecture lacks several important platform capabilities:

1. **Kafka retry-topic chain not implemented** — Failed messages are not retried or dead-lettered; a consumer failure results in silent data loss.
2. **Worker Versioning v2 not implemented** — Long-running workflows cannot be safely patched or migrated without downtime.
3. **Circuit breaker pattern not implemented** — Downstream dependency failures cascade across services with no automatic backpressure.
4. **Fuzz testing expansion needed** — Existing test suites cover happy-path and some edge cases but lack systematic fuzz testing for HTTP parsers, message deserializers, and input validators.

## Scope

| Item | In Scope | Out of Scope |
|------|----------|--------------|
| Kafka retry-topic chain | Implement retry and dead-letter topics for all event consumers | Kafka cluster provisioning |
| Worker Versioning v2 | Design versioning strategy for Temporal workflows | Full migration of existing workflows |
| Circuit breaker | Add circuit breaker middleware for outbound HTTP and gRPC calls | Implementing custom resilience libraries |
| Fuzz testing | Expand fuzz test coverage for customer, notification, and catalog services | Full coverage of all services |

## Success Criteria

- [ ] Kafka consumers have retry-topic support with configurable retry counts
- [ ] Dead-letter topic receives messages that exceed max retries
- [ ] Circuit breaker middleware available and applied to service-to-service calls
- [ ] Fuzz tests exist for customer-service, notification-service, and catalog-service HTTP handlers
- [ ] All new code has corresponding specs in openspec/

## Approach

1. Implement each feature incrementally, starting with fuzz testing (lowest risk)
2. Add circuit breaker as middleware (medium risk)
3. Implement Kafka retry-topic chain (higher complexity)
4. Design Worker Versioning v2 strategy (planning phase)

## Risks

| Risk | Mitigation |
|------|------------|
| Retry-topic increases Kafka partition count | Monitor partition usage; configure retention |
| Circuit breaker adds latency on failure recovery | Use exponential backoff with jitter |
| Fuzz tests may be slow in CI | Run fuzz tests on nightly schedule, not per-commit |
