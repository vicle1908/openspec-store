# Proposal: align-temporal-go-microservices-patterns

## Why

Comprehensive research using our newly adopted `temporal-developer` and `temporal-ops` skills against official Temporal releases (`go.temporal.io/sdk v1.49.0`, `go.temporal.io/api v1.63.7`, `temporalio/cli v1.9.1`) revealed toolchain discrepancies, auxiliary SDK version drift, and missing activity heartbeating across the 8 microservices. Standardizing these patterns ensures rapid inner-loop development, crash-safe long-running activity execution, and unified toolchain definitions across the monorepo.

## What Changes

- Harmonize auxiliary module SDK versions: Upgrade `tests/cross-service-smoke/go.mod` from `go.temporal.io/sdk v1.46.0` to the repo-wide standard `v1.49.0`.
- Reconcile `tools.env` toolchain definitions: Align `TEMPORAL_CLI_VERSION` across service verification configs (`inventory-service`, `shipping-service`, `reporting-service`, `catalog-service`) to match workstation Temporal CLI `v1.9.1` and Server `1.32.1`.
- Standardize Activity Heartbeating: Enforce `HeartbeatTimeout` and `activity.RecordHeartbeat(ctx)` across batch and export activities (`reporting-service`, `inventory-service`) running longer than 60 seconds, mirroring the robust pattern in `customer-service`.
- Introduce Local Dev Server Target: Add `make temporal-dev` to the root `Makefile` allowing developers and agent harnesses to launch an ephemeral, user-scoped `temporal server start-dev` on loopback without Docker dependencies.
- Codify Standalone Activities Guidance: Formulate architectural guidance for evaluating Standalone Activities on single-activity background jobs, avoiding unnecessary workflow history allocation.

## Capabilities

### New Capabilities

- `temporal-service-orchestration-alignment`: Governs activity heartbeating standards, auxiliary SDK version parity, monorepo toolchain harmonization, and inner-loop CLI development server targets across `go-microservices`.

### Modified Capabilities

## Impact

- All service and test modules share identical Temporal SDK dependencies (`v1.49.0` and `v1.63.7`).
- Worker host crashes during batch operations are detected within seconds via heartbeats rather than waiting out full `StartToCloseTimeout` windows.
- Developers and autonomous agents gain a direct inner-loop Make target (`make temporal-dev`).
- Zero breaking changes to existing workflow event history or external gRPC/HTTP APIs.
