# Design: align-temporal-go-microservices-patterns

## Context

The `go-microservices` repository orchestrates distributed sagas across 8 services and 9 task queues using `go.temporal.io/sdk v1.49.0`. While core workflows adhere strictly to hexagonal architecture and AST determinism (validated via `workflowaudit`, `workflowcheck`, and `worker.WorkflowReplayer`), cross-service audits using our newly adopted `temporal-developer` and `temporal-ops` skills identified auxiliary module dependency drift, conflicting toolchain pins in `tools.env`, and absent activity heartbeating in batch workloads. See `proposal.md` for full motivation.

## Goals / Non-Goals

**Goals:**
- Eliminate version drift by aligning auxiliary test modules (`tests/cross-service-smoke`) with repo-wide `go.temporal.io/sdk v1.49.0`.
- Harmonize monorepo toolchain definitions across service `tools.env` files to match workstation Temporal CLI `v1.9.1` and Server `v1.32.1`.
- Enforce activity heartbeating contracts (`HeartbeatTimeout` and `activity.RecordHeartbeat`) for all activities with `StartToCloseTimeout >= 60s` (e.g. `reporting-service` aggregations and `inventory-service` batch releases).
- Provide a first-class `make temporal-dev` inner-loop target in the root `Makefile` using the local `temporal` CLI binary.

**Non-Goals:**
- Rewriting existing order fulfillment saga orchestration or altering public workflow type names.
- Breaking backwards compatibility with existing event history fixtures in `test/replay/fixtures/temporal/`.
- Replacing existing Docker Compose or Kubernetes deployment manifests.

## Decisions

- **Decision 1: Explicit Heartbeat Timeout on Batch Activities**: The Go SDK relies on heartbeats to detect worker process termination before `StartToCloseTimeout` expires. Activities with long execution windows must declare `HeartbeatTimeout` (e.g., 10s to 30s) and call `activity.RecordHeartbeat(ctx, progress)`. The Go SDK internally throttles heartbeat RPCs to 80% of the timeout window, avoiding network churn.
- **Decision 2: Strict Monorepo Version Parity**: All 8 service modules, platform, and test suites must share identical minor releases (`v1.49.0` and `v1.63.7`). Discrepancies in `tests/cross-service-smoke` (currently `v1.46.0`) introduce risk of testing against deprecated SDK behaviors.
- **Decision 3: Zero-Container Local Development Target**: Rather than requiring Docker Compose for quick local development loops, `make temporal-dev` invokes `/opt/homebrew/bin/temporal server start-dev` with persistent SQLite storage, binding to `127.0.0.1:7233` and UI on `127.0.0.1:8233`.
- **Decision 4: Versioning Discipline for Workflow Updates**: Any future workflow structural modifications must follow the 3-step lifecycle using `workflow.GetVersion(ctx, changeID, minSupported, maxSupported)` as codified in `temporal-developer/references/go/versioning.md`.

## Risks / Trade-offs

- **[Risk: Breaking replay on history fixtures]** → *Mitigation*: Run `make temporal-verify` (incorporating `test-temporal-replay.sh`) before and after any changes to verify exact history replay.
- **[Risk: Local dev server port collision]** → *Mitigation*: The `temporal-dev` target uses standard environment overrides (`TEMPORAL_PORT`, `TEMPORAL_UI_PORT`).
