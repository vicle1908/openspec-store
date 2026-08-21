# Design: Reconcile Stale MLflow and OTel Instrumentation Specs

## Context

The `mlflow-otel-integration` and `otel-auto-instrumentation` canonical specs contain normative requirement titles that contradict the implemented behavior and the umbrella `agent-observability-contract`. The implementation (157/157 tests passing on agent-core HEAD `615eef2`) is correct and stable. The specs need reconciliation to match.

## Decisions

### D1: Route-mode replacement for MLflow
The unconditional Collector export mandate is replaced by explicit exclusive route modes: `autolog` (default), `collector` (deployment-gated), `disabled`. Autolog failure does not imply Collector fallback — MLflow tracing is simply treated as disabled.

### D2: Global ownership for Pydantic AI instrumentation
`Agent.instrument_all()` is the canonical global owner. AgentRuntime adds explicit `Instrumentation()` only for fallback or per-agent override. Each logical operation emits exactly one span.

### D3: Spec-only change
No source code, dependencies, deployments, databases, or tests are modified. The implementation already conforms to the reconciled contract.

### D4: Cross-cutting concerns stay in the umbrella
Lifecycle, correlation, privacy, exporter topology, and evaluation linkage remain governed by `agent-observability-contract`.

## Non-Goals

- No Collector activation or deployment validation (follow-up scope)
- No source code changes in agent-core or agent-docs-sync
- No cross-language telemetry work
- No live backend verification

## Rollback
Revert canonical spec synchronization via `git revert` of the archive commit.
