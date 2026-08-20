# Establish Agent Observability Contract

## Why

The agent ecosystem has multiple observability implementations and backend-specific specifications (`otel-auto-instrumentation`, `langfuse-otel-integration`, `mlflow-otel-integration`, `evaluation`, `observability-tests`, `agent-docs-sync-observability`), but process activation, telemetry correlation, privacy, evaluation linkage, exporter ownership, and shutdown behavior are not governed by one enforceable contract. As a result, observability activation is consumer-dependent (agent-docs-sync initializes tracing; agent-core's own CLI does not), evaluation records cannot be linked to traces, MLflow integration has verified defects in exception handling and numeric score aggregation, and duplicate or disconnected telemetry cannot be ruled out.

## What Changes

- Introduce an ecosystem-wide agent observability lifecycle contract covering initialization ownership, idempotency, shutdown flushing, telemetry correlation, privacy, propagation, exporter topology, evaluation linkage, and conformance testing.
- Require every supported process entry point to initialize observability exactly once at its composition root.
- Define the authoritative relationship between explicit Pydantic AI `Instrumentation()` capability and global `Agent.instrument_all()` to prevent duplicate spans.
- Define canonical OTel resource, agent, workflow, run, conversation, tool, and evaluation correlation attributes — reconciling existing `gen_ai.*` standard attributes with `agent_core.*` extensions.
- Require trace identifiers to flow into structured logs (structlog) and evaluation records (`EvalRecord`).
- Define content-capture and field-level redaction requirements, replacing the current coarse boolean controls.
- Require deterministic exporter routing that prevents duplicate Langfuse or MLflow ingestion.
- Correct verified defects: MLflow `_Suppress.__exit__` exception handling and MLflow evaluation pass-rate numeric score semantics.
- Expand observability tests to validate activation, span hierarchy, shutdown flushing, redaction, propagation, and backend degradation.
- Define rollout evidence that distinguishes specified, implemented, tested, runtime-validated, and deployment-validated capabilities.

## Non-Goals

- Building a custom trace storage backend.
- Replacing OpenTelemetry, Langfuse, MLflow, Prometheus, or Grafana.
- Implementing time-travel replay or semantic failure clustering.
- Capturing hidden model reasoning.
- Requiring sensitive prompt or tool payload capture in production.
- Redesigning all existing dashboards.
- Selecting a sampling percentage before production-volume evidence exists.
- Implementing memory, MCP, DBOS, or handoff span instrumentation (separate change).
- Cross-language propagation validation (separate change after this contract is established).

## Capabilities

### New Capabilities

- **`agent-observability-contract`**
  - Defines lifecycle ownership, initialization idempotency, telemetry correlation schema, privacy/redaction policy, exporter topology, evaluation-to-trace linkage, conformance classifications, and rollout evidence requirements.
  - This is the umbrella contract that governs all observability behavior across the agent ecosystem.

### Modified Capabilities

- **`otel-auto-instrumentation`**
  - Clarifies which composition root must initialize observability.
  - Adds initialization-exactly-once requirement and idempotency.
  - Defines interaction between explicit `Instrumentation()` capability and `Agent.instrument_all()` to prevent duplicate spans.
  - Adds shutdown/flush behavior requirements.
  - Adds metrics initialization responsibility.

- **`observability-tests`**
  - Extends beyond LangfuseClient/MLflowClient wrapper unit tests.
  - Adds startup activation conformance tests.
  - Adds span hierarchy assertion tests.
  - Adds duplicate-span detection tests.
  - Adds flush-on-exit tests for short-lived CLI and scheduler processes.
  - Adds redaction/privacy tests.
  - Adds trace-log correlation tests.
  - Adds exporter-unavailable degradation tests.

- **`evaluation`**
  - Adds `trace_id` and optional `span_id` fields to `EvalRecord`.
  - Defines numeric-score pass/fail aggregation semantics (replacing `is True` check).
  - Adds evaluator and dataset version provenance.
  - Adds production-trace-to-regression-dataset linkage expectation.

- **`langfuse-otel-integration`**
  - Establishes authoritative export route (OTel Collector vs direct SDK).
  - Adds duplicate-prevention requirement.
  - Adds backend failure isolation requirement.
  - Adds metadata propagation and privacy requirements.

- **`mlflow-otel-integration`**
  - Establishes canonical trace route and relationship between autolog and collector export.
  - Adds duplicate-prevention requirement.
  - Adds exception isolation requirement (fixing `_Suppress` defect).
  - Adds correct numeric evaluation aggregation semantics.

## Impact

### Ownership Boundaries

| Surface | Owner | Responsibility |
|---------|-------|---------------|
| `agent-core` | agent-core team | Observability SDK lifecycle, canonical attributes, Pydantic AI instrumentation, evaluation linkage, scorer correctness |
| Consumer repos (agent-docs-sync, agent-harness, etc.) | respective teams | Composition-root initialization, graceful shutdown integration |
| `tdt-observability` | operations team | Operational dashboards, retention, SLO presentation |
| Go platform services | platform team | W3C propagation, service-side telemetry conformance |
| Deployment configuration | platform team | Collector routing, batching, retry, backend isolation |
| `openspec-store` | shared | Cross-repository behavioral contract and validation evidence |

### Affected Systems

- `agent-core` CLI and SDK (`foundation/tracing.py`, `sdk/observability.py`, `cli/app.py`)
- `agent-docs-sync` (`cli.py`, `observability/__init__.py`)
- `agent-harness` and DBOS scheduler processes
- Langfuse and MLflow exporters
- OTel Collector deployment configuration
- Evaluation database schema (`agent_memory.eval_metrics`)
- structlog processors (`foundation/logging.py`)
- Kafka propagation tests (Go platform)
- Prometheus/Grafana and Streamlit dashboards (`tdt-observability`)
