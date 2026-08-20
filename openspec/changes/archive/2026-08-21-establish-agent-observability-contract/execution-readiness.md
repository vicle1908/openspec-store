# Execution Readiness: Establish Agent Observability Contract

**Date:** 2026-08-20
**Change:** establish-agent-observability-contract
**Status:** Ready for implementation (with explicit gating conditions)

---

## GO — Core Implementation

These items can proceed immediately after impact analysis confirms blast radius:

| Phase | Item | Repo | Evidence |
|-------|------|------|----------|
| 0.1 | Idempotent `init_observability()` with module-level guard | agent-core | task 2.2 |
| 0.2 | Agent-core CLI composition-root initialization | agent-core | task 2.4 |
| 0.3 | Agent-docs-sync import-side-effect removal | agent-docs-sync | task 2.6 |
| 0.4 | OTel metrics initialization via `configure_metrics()` | agent-core | task 2.3 |
| 0.5 | Instrumentation duplicate-span prevention | agent-core | tasks 3.1–3.5 |
| 0.6 | Trace-log correlation (structlog processor) | agent-core | task 5.1 |
| 0.7 | `EvalRecord` trace linkage (trace_id, span_id) | agent-core | tasks 4.3–4.6 |
| 0.8 | MLflow exception isolation (`_Suppress` fix) | agent-core | tasks 1.1, 4.1 |
| 0.9 | Assertion/task/numeric evaluation reporting | agent-core | tasks 1.2, 4.2 |
| 0.10 | Bounded flush and shutdown | agent-core | tasks 2.2, 6.2 |
| 0.11 | Content-off defaults and minimum credential redaction | agent-core | tasks 5.3–5.5 |
| 0.12 | Conformance tests (activation, idempotency, hierarchy, flush, correlation, redaction, backend isolation, evaluation linkage) | agent-core | tasks 7.1–7.12 |

## NO-GO — Pending Phase 0 Runtime Evidence

These items MUST NOT be implemented until runtime evidence proves the endpoints and active topology:

| Item | Reason | Required Evidence |
|------|--------|-------------------|
| Langfuse Collector mode | `langfuse-web:4317` is a declaration, not proof | OTLP endpoint probe from active Collector |
| MLflow Collector mode | `mlflow-server:5000` is typically HTTP UI, not OTLP/gRPC | OTLP endpoint probe from active Collector |
| Unified Python/Go traces | Two disconnected Collector configs exist | Cross-language trace correlation test |
| Deployment-readiness claims | Endpoints unverified | One exported trace inspected in each backend |
| Collector endpoint promotion to production | Untested at runtime | `make validate-deployment` pass |

## Phase 0 Evidence Checklist

Before any backend routing implementation:

- [ ] Inspect active Collector configuration (which exporters are live?)
- [ ] Probe Langfuse OTLP endpoint (does `langfuse-web:4317` accept OTLP gRPC?)
- [ ] Probe MLflow OTLP endpoint (does `mlflow-server:5000` accept OTLP traces?)
- [ ] Verify `mlflow.pydantic_ai.autolog()` compatibility with installed pydantic-ai v2
- [ ] Export one trace and inspect it in each enabled backend
- [ ] Run duplicate-ingestion test (count span processors, assert one logical operation = one backend trace)
- [ ] Complete consumer entry-point inventory

## Deployment Topology Conclusion

> The repository currently contains at least two different Collector configurations:
>
> 1. `agent-core/otel-collector-config.yaml` — declares Langfuse (`langfuse-web:4317`) and MLflow (`mlflow-server:5000`) exporters for traces, metrics, and logs.
> 2. `go-microservices/deploy/otel-collector-config.yaml` — exports all signals only to the `debug` exporter (local-dev config).
>
> A unified deployment topology has not been demonstrated. Cross-language trace correlation between Python agents and Go services is not execution-ready.

## Consumer Inventory

| Consumer | Uses agent-core | Init confirmed | Phase 0 evidence | Decision |
|----------|:-:|:-:|:-:|---------|
| agent-core CLI (`agent-core`) | — | No | — | In scope (primary target) |
| agent-docs-sync (`docs-sync`) | Yes | Yes, including import side effect | CLI callback calls `init_observability()` | In scope migration |
| agent-harness (`agent-harness`) | Yes | Not found | No observability files | Task 0.8 |
| code-daily-scan (`code-daily-scan`) | Yes | Not found | No observability files | Task 0.8 |
| tdt-observability (`tdt-observability`) | No | No | Operational dashboards only | Out of scope |
| webhook-receiver (`webhook-receiver`) | No | No | structlog only | Out of scope |
| DBOS scheduler workers | Indirect | Unknown | — | Phase 0 inventory |

## Implementation Sequence

```
Phase 0  Evidence capture (no code changes)
         ↓
Phase 1  Regression tests for MLflow _Suppress and CLI activation
         ↓
Phase 2  Lifecycle, idempotency, CLI initialization
         ↓
Phase 3  Langfuse singleton / duplicate prevention
         ↓
Phase 4  Evaluation trace linkage and DB migration
         ↓
Phase 5  Trace-log correlation, privacy, conformance tests
         ↓
Phase 6  Backend route configuration (only after Phase 0 evidence)
```

## Unresolved Semantic Issues (Requiring Approval)

1. **Langfuse singleton risk** — `LangfuseClient.create()` constructs a separate trace-enabled `Langfuse` instance. Implementation task 3.1 must verify they share the singleton or disable tracing on the manual-scoring client. First regression test: count exported span processors.

2. **`span_id` ownership** — `EvalRecord.span_id` will be populated from `EvaluationReport.span_id` (the evaluation-run span), not the ambient OTel context. Multiple cases within one evaluation share one evaluation trace.

3. **MLflow route is not defaulted** — The base spec no longer mandates Collector. Default mode will be selected only after Phase 0 evidence. This means autolog is the current runtime path.

## Final Gate (Run Once)

After all corrections and `execution-readiness.md`:

1. `openspec validate establish-agent-observability-contract --strict --store openspec-store`
2. `openspec status --change establish-agent-observability-contract --store openspec-store`
3. `git status --short` — verify only intended planning artifacts changed
4. `git diff --stat` — verify no source code touched

**Do not run this gate more than once.**
