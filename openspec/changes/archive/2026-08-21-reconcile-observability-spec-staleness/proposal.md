# Proposal: Reconcile Stale MLflow and OTel Instrumentation Specs

## Why

Two older capability specifications prescribe behaviors that contradict the implemented and umbrella-governed observability architecture. The `mlflow-otel-integration` spec mandates unconditional OTLP Collector export for MLflow, while the implementation uses exclusive route modes (`autolog` default, `collector` deferred, `disabled`). The `otel-auto-instrumentation` spec requires every `AgentRuntime` to unconditionally construct an explicit `Instrumentation()` capability, while the implemented and umbrella-governed behavior makes `Agent.instrument_all()` the canonical global owner, with explicit capabilities reserved for conditional override.

## What Changes

- Modify `mlflow-otel-integration` to describe exclusive route modes (`autolog`/`collector`/`disabled`) with `autolog` as default. Preserve scenarios for retained requirements; replace obsolete Collector-only scenarios with route-mode scenarios.
- Modify `otel-auto-instrumentation` to describe global instrumentation ownership via `Agent.instrument_all()`, with explicit runtime capabilities as conditional override, preserving all existing scenarios and adding duplicate-span prevention.
- No new capabilities introduced.
- No source code changes in any repository.

## Non-Goals

- No runtime/source changes in `agent-core` or `agent-docs-sync`.
- No Collector activation or deployment validation.
- No changes to the umbrella `agent-observability-contract`.
- No cross-language telemetry work.
- No live Langfuse/MLflow deployment verification.

## Capabilities

### Modified Capabilities

- `mlflow-otel-integration` — route-mode model replaces unconditional Collector mandate
- `otel-auto-instrumentation` — global ownership replaces unconditional explicit capability

### New Capabilities

- None.

## Impact

- Affected ownership boundaries: `openspec/specs/mlflow-otel-integration/`, `openspec/specs/otel-auto-instrumentation/`
- No source code affected in any repository
- No tests affected
- No deployment changes
- No OpenSpec validation baseline change expected (375 passed, 0 failed)
