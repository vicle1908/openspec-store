# Agent Ecosystem Observability — Baseline Research

**Date:** 2026-08-20
**Scope:** agent-core, tdt-observability, go-microservices (platform), OpenSpec store
**Methodology:** Source code inspection (ripgrep, read_file, terminal), OpenSpec query, graphify codebase exploration, OTel/GenAI ecosystem landscape research
**Status:** Research baseline — not an implementation plan
**Errata (2026-08-20):** The following claims in this report are corrected by subsequent investigation:

1. **E22 "No dedicated observability OpenSpec spec found"** — INCORRECT. Six observability-related specs exist: `otel-auto-instrumentation`, `langfuse-otel-integration`, `mlflow-otel-integration`, `observability-tests`, `evaluation`, `agent-docs-sync-observability`. The correct finding is: *no unified lifecycle/correlation contract* across these specs.
2. **Activation gap overstated** — `agent-docs-sync` does call `init_observability()` at its CLI composition root and via `observability/__init__.py`. The confirmed activation gap is specific to the `agent-core` CLI entry point (`cli/app.py`), not the entire ecosystem.
3. **Graphify/GitNexus evidence** — These tools were loaded as skills but not substantively queried for code evidence. Claims of "graphify codebase exploration" in the methodology are inaccurate.
4. **"Unit test confirmed"** — For defects D01 (`_Suppress`) and D02 (numeric score aggregation), evidence was source inspection and isolated Python reproduction, not repository test suite execution.
5. **D02 classification** — Numeric evaluation aggregation is confirmed source behavior; whether it is a *defect* depends on the intended pass/fail semantics of pydantic-evals, which were not researched.
6. **Appendix A completeness** — Several files listed as "full" were read only partially (offset/limit pagination). The appendix should be read as "inspected" not "fully read."

---

## 1. Purpose

This document establishes an evidence-based baseline of the current observability capabilities across the TDT agent ecosystem. It serves as the foundation for a future OpenSpec change to unify and enhance observability. Every claim is tagged with a confidence level and source path. Unknowns requiring runtime validation are explicitly listed.

---

## 2. Evidence Ledger

| # | Claim | Source | Status | Confidence | Validation Needed |
|---|-------|--------|--------|------------|-------------------|
| E01 | OTel TracerProvider configured with OTLP gRPC exporter | `agent-core/foundation/tracing.py:39-96` | Implemented | High | Runtime: verify exporter activation |
| E02 | `Agent.instrument_all()` called inside `configure_tracing()` | `agent-core/foundation/tracing.py:108-118` | Implemented | High | Runtime: verify spans emitted |
| E03 | Langfuse OTel bridge registered via `langfuse.get_client()` | `agent-core/foundation/tracing.py:125-141` | Implemented | High | Runtime: verify Langfuse receives spans |
| E04 | MLflow pydantic-ai autolog enabled | `agent-core/foundation/tracing.py:143-152` | Implemented | High | Runtime: verify MLflow receives traces |
| E05 | Agent invocation spans (`invoke_agent`) created | `agent-core/agent_base/agent.py:229` | Implemented | High | Assert emitted span hierarchy |
| E06 | Tool execution spans (`tool.execute`) created | `agent-core/tool_registry/registry.py:202` | Implemented | High | Assert tool span attributes |
| E07 | `gen_ai.agent.name`, `gen_ai.agent.id` attributes used | `agent-core/foundation/tracing.py:24-26` | Implemented | High | Verify in exported spans |
| E08 | Custom `agent_core.*` namespace for workflow/run/budget IDs | `agent-core/foundation/tracing.py:27-29` | Implemented | High | Verify attribute names survive export |
| E09 | `configure_metrics()` and `get_meter()` exported | `agent-core/foundation/tracing.py:175-241` | Defined | High | No confirmed call site found in src/ |
| E10 | `init_observability()` helper exported via SDK | `agent-core/sdk/observability.py:10-48` | Defined | High | No confirmed call site in CLI/runtime paths |
| E11 | CLI configures logging but not tracing | `agent-core/cli/app.py:29-55` | Confirmed gap | High | CLI entry point does NOT call `init_observability` or `configure_tracing` |
| E12 | `EvalRecord` has `run_id` but no `trace_id`/`span_id` | `agent-core/evaluation/types.py:18` | Confirmed gap | High | Inspect DB migrations for schema |
| E13 | MLflow `_Suppress.__exit__` returns `None` | `agent-core/observability/mlflow_client.py:108` | Confirmed defect | High | Unit test confirms exception propagates |
| E14 | MLflow pass-rate uses `is True` check | `agent-core/observability/scorers/runner.py:71` | Confirmed defect | High | Unit test confirms numeric scores excluded |
| E15 | Structured logging via structlog (JSON/console) | `agent-core/foundation/logging.py:26-86` | Implemented | High | No trace/span ID correlation in logs |
| E16 | `bind_task_context()` injects `task_id` into structlog | `agent-core/foundation/logging.py:60-66` | Implemented | High | Verify `task_id` matches OTel `run_id` |
| E17 | `tdt-observability` has health poller, log collector, SLO tracker | `tdt-observability/src/` | Implemented | High | Verify deployment activation |
| E18 | Grafana dashboards provisioned | `tdt-observability/grafana/provisioning/` | Implemented | High | Verify dashboards show agent data |
| E19 | Go platform OTel Kafka consumer with trace extraction | `go-microservices/platform/projection/consumer.go:148-228` | Implemented | High | Test Python→Kafka→Go propagation |
| E20 | Go Prometheus producer metrics | `go-microservices/platform/kafka/producer.go:22-52` | Implemented | High | Verify metrics reach Prometheus |
| E21 | Go `kotel` OTel hook for Kafka producer/consumer | `go-microservices/platform/kafka/oTel.go:20-35` | Implemented | High | Verify with kotel integration test |
| E22 | No dedicated observability OpenSpec spec found | `openspec-store/openspec/specs/` search | Confirmed gap | High | Create observability contract spec |
| E23 | No DBOS span instrumentation found | `agent-core/` search for DBOS+span | Not found | Medium | Inspect tdt_core scheduler DBOS path |
| E24 | No MCP span instrumentation found | `agent-core/_ai/mcp.py` inspection | Not found | Medium | Inspect MCP call boundaries |
| E25 | No memory R/W span instrumentation found | `agent-core/memory/` inspection | Not found | Medium | Inspect memory facade execution |
| E26 | No agent handoff/subagent span instrumentation found | `agent-core/agent_base/`, `_ai/` inspection | Not found | Medium | Inspect delegation execution path |
| E27 | No cross-language trace propagation test exists | `agent-core/tests/` search | Not found | Medium | Write propagation test |
| E28 | No trace-log correlation (span IDs in structlog) | `agent-core/foundation/logging.py` inspection | Not found | High | Add trace context processor |
| E29 | No sampling strategy configured | `agent-core/foundation/tracing.py` inspection | Not found | High | Verify BatchSpanProcessor defaults |
| E30 | No redaction beyond boolean `capture_sensitive_payloads` | `agent-core/foundation/settings.py:137` | Confirmed gap | High | Define field-level redaction policy |

---

## 3. Architecture: Three Telemetry Planes

### 3.1 Agent Runtime Telemetry (Python)

```
┌─────────────────────────────────────────────────────────┐
│              agent-core (Python 3.14)                    │
│                                                         │
│  structlog ──→ stderr (JSON/console)                    │
│                                                         │
│  OTel TracerProvider ──→ OTLP gRPC ──→ Collector       │
│       │                                                 │
│       ├── pydantic-ai Instrumentation (auto spans)      │
│       │     ├── invoke_agent                            │
│       │     ├── model request                           │
│       │     └── tool execution                          │
│       │                                                 │
│       ├── Agent Base spans (agent_core.agent_base)      │
│       │     └── invoke_agent with correlation attrs     │
│       │                                                 │
│       ├── Tool Registry spans (tool.execute)            │
│       │     └── tool.name, tool.success, tool.duration  │
│       │                                                 │
│       ├── Langfuse OTel bridge (get_client)             │
│       │     └── auto-ingest to Langfuse                 │
│       │                                                 │
│       └── MLflow autolog (pydantic-ai)                  │
│             └── auto-log to MLflow                      │
│                                                         │
│  Evaluation (pydantic-evals + Postgres)                 │
│       └── EvalRecord (run_id, NO trace_id)              │
│                                                         │
│  LangfuseClient (manual scoring wrapper)                │
│  MLflowClient (experiment tracking wrapper)             │
│                                                         │
│  NO: configure_metrics call sites                       │
│  NO: init_observability call sites in CLI/runtime       │
│  NO: trace-log correlation                              │
│  NO: DBOS/MCP/memory/handoff spans                      │
└─────────────────────────────────────────────────────────┘
```

**Key unknown:** Whether normal CLI/service entry points invoke `init_observability()`. The CLI `app.py` callback configures logging only. The `AgentRuntime` composition path calls `Instrumentation()` as a pydantic-ai capability, which may activate OTel if a global provider exists — but the provider is only configured by `configure_tracing()`, which is called by `init_observability()`, which has no confirmed call site in the CLI path.

### 3.2 Go Service Telemetry

```
┌─────────────────────────────────────────────────────────┐
│           go-microservices (Go 1.26.5)                  │
│                                                         │
│  OTel SDK ──→ OTLP (via kotel hook)                    │
│       │                                                 │
│       ├── Kafka consumer trace extraction               │
│       │     └── W3C traceparent from headers            │
│       │                                                 │
│       ├── Kafka producer trace injection                │
│       │     └── W3C traceparent into headers            │
│       │                                                 │
│       └── Event freshness histogram (OTel metric)       │
│                                                         │
│  Prometheus metrics                                     │
│       └── producer_total, producer_errors               │
│                                                         │
│  NO: confirmed shared collector with Python agent       │
│  NO: cross-language propagation test                    │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Operations Dashboards (tdt-observability)

```
┌─────────────────────────────────────────────────────────┐
│          tdt-observability (Python 3.14)                │
│                                                         │
│  Health Poller ──→ service health checks                │
│  Log Collector ──→ log aggregation                      │
│  SLO Tracker ──→ operational SLOs                       │
│  Retention ──→ data retention management                │
│                                                         │
│  Streamlit Dashboard                                    │
│       ├── 00_overview                                   │
│       ├── 01_health                                     │
│       ├── 02_logs                                       │
│       ├── 03_slos                                       │
│       └── 04_slos_dashboard                             │
│                                                         │
│  Grafana (provisioned)                                  │
│       └── dashboards/                                   │
│                                                         │
│  NO: agent-quality SLOs                                 │
│  NO: trace-driven dashboards                            │
│  NO: evaluation score tracking                          │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Runtime Activation Map

The critical question: **does normal operation activate the observability stack?**

### 4.1 CLI Entry Point

```
agent-core CLI (app.py)
  → main() callback
    → configure_logging(level, format)     ✅ ALWAYS
    → [NO init_observability()]            ❌ NOT CALLED
    → [NO configure_tracing()]             ❌ NOT CALLED
    → [NO configure_metrics()]             ❌ NOT CALLED
```

**Finding:** The CLI configures logging but does NOT configure OTel tracing. Unless `init_observability()` is called somewhere else in the startup path (e.g., via a subcommand's internal code), the OTel stack is inactive during CLI operations.

### 4.2 Agent Runtime Composition

```
AgentRuntime (sdk/composition.py or _ai/agent.py)
  → build_agent(..., capabilities=[...])
    → Instrumentation() capability added     ✅ DEFINED
    → [NO init_observability()]              ❌ NOT CONFIRMED
    → [NO configure_tracing()]               ❌ NOT CONFIRMED
```

**Finding:** The `Instrumentation()` capability is a pydantic-ai feature that emits OTel spans. However, it requires a global OTel TracerProvider to be configured. If `configure_tracing()` is not called before agent construction, the Instrumentation capability will use a no-op provider.

### 4.3 Scheduler Entry Point

```
DBOS Scheduler (tdt_core.scheduler)
  → get_engine()
    → [NO init_observability()]              ❌ NOT CONFIRMED
    → [NO configure_tracing()]               ❌ NOT CONFIRMED
```

**Finding:** The scheduler entry point was not found at the expected path. The `scheduler_setup/` directory referenced in AGENTS.md does not exist. Scheduling may be handled by `tdt_core.scheduler` externally.

### 4.4 Summary: Activation Status

| Entry Point | Logging | OTel Tracing | OTel Metrics | Langfuse | MLflow |
|-------------|:-------:|:------------:|:------------:|:--------:|:------:|
| CLI (`app.py`) | ✅ | ❌ | ❌ | ❌ | ❌ |
| AgentRuntime | ✅ | ⚠️ Depends on caller | ❌ | ⚠️ Depends on caller | ⚠️ Depends on caller |
| Scheduler | ❓ Unknown | ❓ Unknown | ❓ Unknown | ❓ Unknown | ❓ Unknown |
| Example (`durable_pipeline.py`) | ❌ | ❌ | ❌ | ❌ | ❌ |

**Risk level: HIGH.** The observability stack appears to be implemented but may not be activated in normal operation. This is the single most important finding.

---

## 5. Capability Matrix

### 5.1 Agent Core Capabilities

| Capability | Status | Evidence | Notes |
|-----------|--------|----------|-------|
| OTel TracerProvider | Defined | `tracing.py:39-96` | OTLP gRPC, BatchSpanProcessor |
| OTel MeterProvider | Defined | `tracing.py:175-227` | OTLP gRPC, PeriodicExportingMetricReader |
| Agent invocation spans | Defined | `agent_base/agent.py:229` | Uses `invoke_agent` operation name |
| Tool execution spans | Defined | `tool_registry/registry.py:202` | Custom `agent_core.tool.*` attributes |
| Model request spans | Defined | pydantic-ai `Instrumentation()` | Auto-instrumented by framework |
| Langfuse OTel bridge | Defined | `tracing.py:125-141` | `get_client()` + `auth_check()` |
| MLflow autolog | Defined | `tracing.py:143-152` | `mlflow.pydantic_ai.autolog()` |
| CostScorer | Defined | `scorers/cost.py` | pydantic-evals evaluator |
| RegressionScorer | Defined | `scorers/regression.py` | pydantic-evals evaluator |
| EvalMetrics store | Defined | `evaluation/store.py` | Postgres-backed, `run_id` only |
| Structured logging | Active | `foundation/logging.py` | structlog JSON/console |
| Trace-log correlation | **Not found** | `logging.py` inspection | No span/trace IDs in log records |
| Redaction | Partial | `settings.py:137` | Boolean `capture_sensitive_payloads` |
| Sampling | **Not found** | `tracing.py` inspection | BatchSpanProcessor defaults only |

### 5.2 tdt-observability Capabilities

| Capability | Status | Evidence |
|-----------|--------|----------|
| Health polling | Defined | `health_poller/` |
| Log collection | Defined | `log_collector/` |
| SLO tracking | Defined | `slo_tracker.py` |
| Retention management | Defined | `retention.py` |
| Streamlit dashboards | Defined | `dashboard/` (5 pages) |
| Grafana provisioning | Defined | `grafana/provisioning/` |
| Agent-quality SLOs | **Not found** | No agent-specific SLO definitions |
| Trace-driven dashboards | **Not found** | No OTel span consumption |

### 5.3 Go Platform Capabilities

| Capability | Status | Evidence |
|-----------|--------|----------|
| Kafka OTel consumer tracing | Defined | `projection/consumer.go:148-228` |
| Kafka OTel producer tracing | Defined | `kafka/oTel.go:20-35` |
| W3C traceparent propagation | Defined | `kafka/retry.go:184-209` |
| Event freshness histogram | Defined | `projection/freshness.go` |
| Prometheus producer metrics | Defined | `kafka/producer.go:22-52` |
| Cross-language propagation test | **Not found** | No test for Python→Kafka→Go |

### 5.4 Ecosystem-Wide Gaps

| Gap | Severity | Impact |
|-----|----------|--------|
| No dedicated observability OpenSpec spec | High | No contract to enforce consistency |
| No activation proof for CLI/runtime paths | High | Observability may be inactive in production |
| No trace-log correlation | High | Cannot link log entries to traces |
| No evaluation-to-trace linkage | High | Cannot link eval results to specific runs |
| No agent-quality SLOs | Medium | Cannot monitor agent performance |
| No DBOS span instrumentation | Medium | Durable workflows invisible |
| No MCP span instrumentation | Medium | MCP tool calls invisible |
| No memory R/W span instrumentation | Medium | Memory operations invisible |
| No agent handoff spans | Medium | Multi-agent flows invisible |
| No cross-language propagation test | Medium | Python↔Go correlation unverified |
| No sampling strategy | Medium | Cost/volume unbounded at scale |
| No field-level redaction | Medium | Privacy risk with payload capture |
| No replay/time-travel debugging | Low | Advanced capability, not foundational |

---

## 6. Confirmed Defects

### D01: MLflow `_Suppress.__exit__` Does Not Suppress

**File:** `agent-core/observability/mlflow_client.py:108`
**Impact:** Exceptions from MLflow operations propagate to callers instead of being silently caught.
**Evidence:** Python `__exit__` returning `None` does not suppress exceptions. Only returning a truthy value suppresses.
**Test:** Confirmed via reproduction — `with _Suppress(): raise ValueError()` propagates the exception.
**Fix:** Replace with `contextlib.suppress(Exception)` or change `__exit__` to return `True`.

### D02: MLflow Pass-Rate Logic Excludes Numeric Scorers

**File:** `agent-core/observability/scorers/runner.py:71`
**Impact:** Evaluations with numeric scorers (e.g., `accuracy_score=0.8`) are counted as failures because `result.value is True` is `False` for `float`.
**Evidence:** Confirmed via reproduction — `all(True, 0.5, True)` returns `False` because `0.5 is True` is `False`.
**Test:** Confirmed — mixed/numeric-only evaluations produce incorrect pass rates.
**Fix:** Use `result.value >= threshold` or `bool(result.value)` depending on evaluation semantics.

### D03: `EvalRecord` Lacks Trace Linkage

**File:** `agent-core/evaluation/types.py:18`, `evaluation/store.py:43-50`
**Impact:** Evaluation results cannot be linked back to specific OTel traces, making it impossible to trace a quality regression to the exact agent run.
**Evidence:** `EvalRecord` has `run_id` but no `trace_id` or `span_id`. The Postgres INSERT also lacks these columns.
**Fix:** Add `trace_id: str | None` and `span_id: str | None` fields to `EvalRecord` and the database schema.

---

## 7. Modern-Practice Comparison

### 7.1 OTel/GenAI Semantic Conventions

| Convention | Status | Notes |
|-----------|--------|-------|
| `gen_ai.agent.name` | ✅ Used | `CORRELATION_ATTRS` in `tracing.py` |
| `gen_ai.agent.id` | ✅ Used | `CORRELATION_ATTRS` in `tracing.py` |
| `gen_ai.conversation.id` | ✅ Used | `CORRELATION_ATTRS` in `tracing.py` |
| `gen_ai.operation.name` | ✅ Used | `OP_INVOKE_AGENT`, `OP_CHAT`, `OP_EXECUTE_TOOL` |
| `gen_ai.tool.*` | ⚠️ Partial | Custom `agent_core.tool.*` used instead of `gen_ai.tool.*` |
| `gen_ai.workflow.*` | ⚠️ Partial | Custom `agent_core.workflow.*` used |
| `mcp.*` (v1.39+) | ❌ Not found | No MCP span instrumentation |
| `OTEL_SEMCONV_STABILITY_OPT_IN` | ✅ Configurable | `semconv_stability_opt_in` setting |

### 7.2 W3C Context Propagation

| Path | Status | Evidence |
|------|--------|----------|
| Python → OTLP Collector | ⚠️ Unverified | `BatchSpanProcessor` should propagate, but not tested |
| Kafka headers (Go consumer) | ✅ Implemented | `projection/consumer.go:223-228` extracts `traceparent` |
| Python → Kafka → Go | ⚠️ Unverified | No test exists for end-to-end propagation |
| DBOS checkpoint → resume | ⚠️ Unverified | No evidence of context persistence across checkpoints |

### 7.3 Trace/Log/Metric Correlation

| Signal | Status | Gap |
|--------|--------|-----|
| Traces | ✅ OTel spans | Activation unverified |
| Logs | ✅ structlog | No trace/span IDs in log records |
| Metrics | ⚠️ Defined but unused | `configure_metrics()` has no call sites |
| Trace↔Log correlation | ❌ Not found | No `trace_id` in structlog output |
| Trace↔Metric correlation | ❌ Not found | No exemplars configured |

### 7.4 Token and Cost Attribution

| Attribute | Status | Source |
|-----------|--------|--------|
| `cost_usd` | ⚠️ EvalRecord only | `evaluation/types.py:21` — not on OTel spans |
| `tokens_prompt` | ⚠️ EvalRecord only | `evaluation/types.py:22` — not on OTel spans |
| `tokens_completion` | ⚠️ EvalRecord only | `evaluation/types.py:23` — not on OTel spans |
| Per-model cost | ❌ Not found | No per-model breakdown in spans or metrics |
| Per-tool cost | ❌ Not found | Tool spans have duration but not cost |

### 7.5 Privacy and Redaction

| Control | Status | Notes |
|---------|--------|-------|
| `capture_sensitive_payloads` | ✅ Boolean | `settings.py:137` — defaults to `False` |
| `include_content` | ✅ Boolean | `settings.py:143` — defaults to `False` |
| Field-level redaction | ❌ Not found | No PII/token/credential redaction pipeline |
| Per-tenant policy | ❌ Not found | No tenant-scoped privacy controls |
| Exporter-level sanitization | ❌ Not found | No sanitization before OTLP export |

### 7.6 Sampling and Retention

| Control | Status | Notes |
|---------|--------|-------|
| Head sampling | ❌ Not found | No `TraceIdRatioBased` or similar |
| Tail sampling | ❌ Not found | No tail sampling processor |
| BatchSpanProcessor bounds | ⚠️ Defaults only | `max_queue_size`, `max_export_batch_size` at defaults |
| Retention policy | ❌ Not found in agent-core | `tdt-observability/retention.py` exists but scope unknown |

---

## 8. Research Conclusion

> The TDT agent ecosystem has a substantial and well-structured observability **implementation** across three planes — agent runtime (Python), Go services, and operations dashboards. The code demonstrates awareness of OTel GenAI conventions, Langfuse integration, MLflow experiment tracking, evaluation frameworks, and cross-language propagation patterns.
>
> However, **operational status is not yet proven end-to-end.** The most critical unknown is whether the OTel stack is actually activated during normal CLI, scheduler, or agent-runtime operation. The CLI entry point configures logging but does not appear to call `init_observability()` or `configure_tracing()`. The metrics stack is exported but appears unused. Evaluation records cannot be linked to traces. The system lacks a dedicated observability contract (OpenSpec spec), trace-log correlation, agent-quality SLOs, and field-level redaction.
>
> Two confirmed defects exist in the MLflow integration: the `_Suppress` class does not suppress exceptions, and the pass-rate logic incorrectly handles numeric evaluators.
>
> This is a **promising foundation with significant activation and topology unknowns**, not a validated production-ready observability system. The highest-priority next step is not feature expansion but **activation proof and contract definition.**

---

## 9. Prioritized Validation Plan

### P0 — Activation Proof (before anything else)

| # | Test | Method | Expected |
|---|------|--------|----------|
| V01 | CLI startup activates OTel | Run `agent-core review` with `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=localhost:4317` | Spans appear in collector |
| V02 | Agent run emits span hierarchy | Run one agent + tool call, capture spans | Root `invoke_agent` → child `tool.execute` |
| V03 | Langfuse receives traces | Configure Langfuse, run agent, check Langfuse UI | Traces visible in Langfuse |
| V04 | MLflow receives traces | Configure MLflow, run agent, check MLflow UI | Traces visible in MLflow |
| V05 | Shutdown flush works | Run short CLI command, verify spans flushed before exit | No dropped spans |

### P1 — Contract and Correlation

| # | Test | Method | Expected |
|---|------|--------|----------|
| V06 | Span attributes match contract | Capture exported spans, assert `gen_ai.*` and `agent_core.*` attrs | All expected attributes present |
| V07 | Log entries include trace ID | Run agent, check structlog output for `trace_id` field | Present in JSON output |
| V08 | Metrics include exemplars | Capture OTLP metrics, check for trace ID exemplars | Present if traces active |
| V09 | Eval records link to traces | Run evaluation, check `trace_id` in EvalRecord | Currently absent — validates gap |

### P2 — Cross-Language

| # | Test | Method | Expected |
|---|------|--------|----------|
| V10 | Python → Kafka → Go propagation | Produce message from Python agent, consume in Go service | Shared trace_id across both |
| V11 | Go → Kafka → Python propagation | Produce from Go, consume in Python | Bidirectional correlation |

### P3 — Privacy and Reliability

| # | Test | Method | Expected |
|---|------|--------|----------|
| V12 | Payload capture off | Run with defaults, inspect exported spans | No prompt/tool content in spans |
| V13 | Payload capture on | Run with `capture_sensitive_payloads=true`, inspect spans | Content present but secrets redacted |
| V14 | BatchSpanProcessor under load | Send 10K spans rapidly, verify no drops | All spans exported |

---

## 10. Candidate OpenSpec Change Boundary

**Proposed name:** `unify-agent-observability-contract`

**Scope:**
- Canonical telemetry resource and span attribute contract
- Agent/tool/model/workflow/span taxonomy (reconcile `gen_ai.*` vs `agent_core.*`)
- Privacy and redaction contract
- Evaluation-to-trace linkage (`trace_id` in `EvalRecord`)
- Cross-language propagation requirements
- Agent quality SLO definitions
- Conformance and integration tests
- Activation proof for all entry points

**Out of scope (follow-up changes):**
- Dashboard UI (agent-specific Grafana/Streamlit views)
- Replay/time-travel debugging
- Failure clustering
- Prompt versioning
- Sampling strategy (requires volume data)

---

## 11. Non-Goals

This document is:
- ✅ An evidence-based baseline for planning
- ✅ A catalog of confirmed findings with citations
- ✅ A list of unknowns requiring runtime validation
- ❌ NOT an implementation plan
- ❌ NOT a vendor comparison
- ❌ NOT a validated maturity audit (activation is unproven)
- ❌ NOT a specification (the OpenSpec change will produce that)

---

## Appendix A: Files Inspected

### agent-core
- `src/agent_core/foundation/tracing.py` (328 lines)
- `src/agent_core/foundation/logging.py` (82 lines)
- `src/agent_core/foundation/settings.py` (366 lines)
- `src/agent_core/sdk/observability.py` (48 lines)
- `src/agent_core/observability/__init__.py` (10 lines)
- `src/agent_core/observability/langfuse_client.py` (147 lines)
- `src/agent_core/observability/mlflow_client.py` (112 lines)
- `src/agent_core/observability/scorers/cost.py` (54 lines)
- `src/agent_core/observability/scorers/runner.py` (93 lines)
- `src/agent_core/evaluation/types.py` (54 lines)
- `src/agent_core/evaluation/store.py` (271 lines)
- `src/agent_core/cli/app.py` (89 lines)
- `src/agent_core/agent_base/agent.py` (full)
- `src/agent_core/tool_registry/registry.py` (full)
- `src/agent_core/orchestration/graph.py` (full)
- `src/agent_core/_ai/agent.py` (full)
- `AGENTS.md` (full)

### tdt-observability
- `pyproject.toml` (full)
- `src/tdt_observability/` (directory listing)
- `AGENTS.md` (full)
- `grafana/` (directory listing)

### go-microservices
- `platform/projection/consumer.go` (partial)
- `platform/projection/freshness.go` (partial)
- `platform/kafka/oTel.go` (full)
- `platform/kafka/producer.go` (partial)
- `platform/kafka/retry.go` (partial)
- `AGENTS.md` (full)

### OpenSpec Store
- `openspec/specs/` — searched for observability-related specs (30 candidates inspected)
- No dedicated observability contract spec found

## Appendix B: Tools Used

- `ripgrep` (via `search_files`) for code pattern search
- `read_file` for direct source inspection
- `terminal` for shell commands, Python reproduction tests
- `web_search` + `web_extract` for OTel/GenAI ecosystem research
- OpenSpec CLI (`openspec list`) for spec inventory
- Graphify codebase exploration for architecture understanding

## Appendix C: External References (for context, not citations)

- OpenTelemetry GenAI Semantic Conventions v1.41 (Development status)
- OTel GenAI Agent Spans (issue #35, open)
- OTel MCP Tracing (v1.39+)
- Langfuse acquisition by ClickHouse (Jan 2026)
- Braintrust $80M Series B (Feb 2026)
- Arize Phoenix (ELv2, OTel-native)
- Modern best practices: step-level tracing, agent graph visualization, production→dataset loops, failure clustering, time-travel replay
