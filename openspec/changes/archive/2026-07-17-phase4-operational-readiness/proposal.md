# Phase 4: Operational Readiness

**Status:** Proposed
**Date:** 2026-07-17
**Owner:** engineering

## Summary

Phase 4 addresses operational gaps identified in the Phase 2/3 audits: the broker UI is absent from the tools overlay, rollback rehearsal does not exist, no service runbooks are present, agent config files are unwired, and the payment-service Dockerfile lacks modern build features. These gaps reduce operator confidence and increase mean-time-to-recovery.

## Problem Statement

The current architecture has several operational readiness gaps:

1. **Broker UI missing from tools overlay** — The `compose-tools-profile` spec requires `kafbat/kafka-ui` but the container is not defined in `deploy/docker-compose.tools.yaml`.
2. **No rollback rehearsal script** — There is no automated way to verify that a release can be rolled back safely, making production rollbacks a manual and error-prone process.
3. **No service runbooks** — Operators lack step-by-step recovery procedures for each service; the only runbooks are agent-memory-related.
4. **Agent config files not wired** — `.agent/`, `.claude/`, `.codex/`, `.cursor/`, `.factory/`, `.kilo/`, `.kimi/`, `.kiro/`, `.omp/`, `.opencode/`, `.pi/` directories are untracked and not documented.
5. **Payment-service Dockerfile less mature** — `Dockerfile.payment-service` lacks `--platform=$BUILDPLATFORM`, `-pgo=auto`, `HEALTHCHECK`, and cache mounts that other service Dockerfiles already have.

## Capabilities

| ID | Capability | Affected Boundary |
|----|-----------|-------------------|
| `kafka-ui-tools-overlay` | Add kafbat/kafka-ui to tools overlay | Platform / Kafka tooling |
| `rollback-rehearsal` | Automated rollback rehearsal script | Operations / CI |
| `operational-runbooks` | Per-service runbook templates | Operations / Documentation |
| `payment-dockerfile-maturity` | Modernize payment-service Dockerfile | Platform / Build |

## Non-Goals

- Full agent configuration wiring (tracked separately as a platform concern)
- Kubernetes manifest generation (Phase 3 scope)
- Circuit breaker or retry-topic implementation (Phase 5 scope)

## Approach

1. Implement each capability incrementally, ordered by dependency
2. Kafka UI overlay is a low-risk addition with existing spec requirements
3. Rollback script is standalone and testable in isolation
4. Runbooks provide templates that services can adopt incrementally
5. Dockerfile modernization follows the canonical notification-service pattern

## Risks

| Risk | Mitigation |
|------|------------|
| kafka-ui image lacks arm64 manifest | Pinned tag validated by `make verify-images` |
| Rollback script may not cover all failure modes | Script is a starting point; runbooks document manual escape hatches |
| Dockerfile changes may break existing builds | Test locally with `docker build` before merging |

## Compatibility

- No API contract changes
- No database migration changes
- No runtime behavior changes
- Tooling overlay additions are additive and profile-gated
