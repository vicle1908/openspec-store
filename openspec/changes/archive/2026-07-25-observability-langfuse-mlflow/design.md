## Context

agent-core is a Python 3.14 agent runtime with 10 capabilities, 451 tests, built on Pydantic AI v2 + LangGraph. The current observability stack consists of:

- **OTel tracing** (`foundation/tracing.py:39-106`): GenAI semantic conventions, OTLP gRPC export to configurable endpoint via `configure_tracing()`. Uses `ObservabilitySettings.otel_endpoint` (env prefix `OTEL_`). No-op tracer when endpoint is empty.
- **Hook packs** (`agent_base/hooks/builtins.py`): `otel_metrics` (per-tool latency via OTel Histogram/Counter), `structured_audit` (AuditRecord list + JSONL logging), `cost_tracker` (hooks into `HookPoint.MODEL_REQUEST` AFTER, tracks `LLMUsage.cost_usd`), `approval_gate` (blocks dangerous tools). All registered via `register_pack()`.
- **BaseAgent.run()** (`agent_base/agent.py:177-349`): Emits OTel span via `tracer.start_as_current_span(OP_INVOKE_AGENT)`. Context dict contains `{run_id, correlation_id, task, agent_name, model}`. Fires hooks at `fire_before(HookPoint.RUN)` and `fire_after(HookPoint.RUN)`.
- **EvalMetrics** (`evaluation/store.py:16-271`): Custom Postgres-backed evaluation with `record()` (INSERT into `agent_memory.eval_metrics`), `query()` (SELECT with aggregation), `compare()` (baseline vs current), `regressions()` (threshold-based: latency >20%, success_rate <-10%). EvalRecord as canonical data model.
- **structlog** (`foundation/logging.py`): Console/JSON structured logging with bound context.
- **compose.yaml**: 3 services: `postgres` (18.4-trixie), `app` (agent-core local dev), `scheduler` (tdt-scheduler).

Problems: No visual trace explorer, no experiment comparison UI, no prompt versioning, no LLM-as-judge evaluation, fragmented cost tracking, no regression detection beyond simple thresholds.

**Repo affected:** agent-core (`/Users/lekhanhvinh/Developer/tdt/agent-core/`)

## Validated Versions (as of July 2026)

| Component | Version | Docker Image | Python Package |
|-----------|---------|-------------|----------------|
| Langfuse Server | 3.219 | `langfuse/langfuse:3.219` | N/A (server) |
| Langfuse Python SDK | 4.14.1 | N/A | `langfuse>=4.14.0,<5` |
| MLflow Server | 3.14.0 | `ghcr.io/mlflow/mlflow:3.14.0` | `mlflow>=3.14.0,<4` |
| OTel Collector | 0.157.0 | `otel/opentelemetry-collector-contrib:0.157.0` | N/A |
| ClickHouse | latest | `clickhouse/clickhouse-server:latest` | N/A |
| PostgreSQL | 16 | `postgres:16` | N/A |
| Redis | 7-alpine | `redis:7-alpine` | N/A |
| MinIO | latest | `minio/minio:latest` | N/A |

**Key SDK syntax notes (validated from official docs):**
- Langfuse v4: `get_client()`, `start_as_current_observation(as_type="span"/"generation")`, `propagate_attributes()`, `score_trace()`
- MLflow 3.14: `mlflow.genai.evaluate()`, `@scorer` decorator, `mlflow.pydantic_ai.autolog()`, `mlflow.agent.setup`

## Goals / Non-Goals

**Goals:**
- Production-grade observability with visual trace exploration (Langfuse)
- Experiment tracking with parameter comparison and regression detection (MLflow)
- Prompt versioning, A/B testing, and optimization (MLflow Prompt Registry)
- LLM-as-judge and code-based evaluation framework (both Langfuse scores + MLflow scorers)
- Self-hosted via Docker Compose (no Kubernetes, no cloud dependencies)
- All data stored locally (MinIO for S3-compatible storage, PostgreSQL, ClickHouse)
- Extensible routing via OTel Collector (add backends without code changes)
- Backward-compatible migration from EvalMetrics (dual-write → validate → drop)

**Non-Goals:**
- Migrate scheduling, memory, or orchestration modules (unchanged)
- Replace structlog (kept for application-level logging, separate from trace data)
- Replace existing OTel span creation (just re-routed through Collector)
- Kubernetes deployment (Docker Compose only for now)
- Cloud deployment (nhà cung cấp dịch vụ AI, AWS, GCP, Azure — not yet)
- Logfire self-hosted (K8s-only, Enterprise license — future option via Collector routing)
- Real-time alerting pipelines (Langfuse/MLflow UI is sufficient initially)
- Multi-tenant isolation (single-team deployment)

## Decisions

### D1: Langfuse for observability, MLflow for experiment tracking

**Decision:** Use Langfuse as the primary observability backend (traces, scores, cost, dashboards) and MLflow as the experiment tracking backend (experiments, prompts, evaluation, model registry).

**Rationale:** Langfuse is MIT-licensed, OTel-native, has native Pydantic AI integration via @observe(), and provides LLM-specific features (conversation replay, token tracking, cost dashboards, score analytics). MLflow provides the experiment tracking, prompt registry with A/B testing, prompt optimization (GEPA/DSPy), and the most comprehensive GenAI evaluation framework (Agent GPA, TruLens integration, custom @scorer). They are complementary, not competing.

**Alternatives considered:**
- Logfire only: K8s-only self-hosted, Enterprise license. Rejected for Docker Compose constraint.
- SigNoz only: General observability, no AI-native features (no conversation replay, no prompt management). Rejected for LLM-specific needs.
- MLflow only: Experiment tracking is strong, but trace visualization and real-time dashboards are weaker than Langfuse. MLflow's prompt management is thin (no deployment labels, no A/B testing UI). Rejected for observability gaps.
- Langfuse only: Strong on observability, but experiment comparison and prompt optimization are less mature than MLflow. Rejected for experiment tracking gaps.

### D2: OTel Collector as routing layer

**Decision:** Insert an OpenTelemetry Collector between agent-core and observability backends. Agent-core exports to Collector via OTLP; Collector routes to Langfuse.

**Rationale:** Decouples application from backend. Adding Logfire Cloud, SigNoz, or any OTLP-compatible backend requires only Collector config changes — zero code modifications. The Collector also handles batching, filtering, and retry logic.

**Alternatives considered:**
- Direct OTLP to Langfuse: Simpler, but tightly couples to one backend. Rejected for extensibility.
- Dual SDK (Langfuse SDK + OTel SDK): Both emit independently. Rejected for duplication and inconsistency.

### D3: Keep EvalRecord as canonical data model

**Decision:** Retain EvalRecord (evaluation/types.py) as the canonical data model for agent run metrics. Log its fields as Langfuse trace attributes/scores and MLflow params/metrics.

**Rationale:** EvalRecord is a clean, well-defined Pydantic model. It maps naturally to both Langfuse traces and MLflow runs. Keeping it avoids breaking existing code that constructs EvalRecord instances. The migration is in the storage backend, not the data model.

**Alternatives considered:**
- Replace EvalRecord with Langfuse-native models: Would break existing code and lose the clean abstraction. Rejected.
- Replace EvalRecord with MLflow-native models: Same issue. Rejected.

### D4: Separate Postgres databases per service + shared local MinIO

**Decision:** Langfuse gets its own Postgres database (`langfuse-postgres`), MLflow gets its own (`mlflow-postgres`), separate from the existing `agent_core` database. MinIO is shared between Langfuse and MLflow (single instance, separate buckets: `langfuse` and `mlflow`). All storage is local — no cloud dependencies.

**Rationale:** Isolation prevents schema conflicts, allows independent backups/restores, and simplifies upgrades. Langfuse v3 requires its own Postgres for metadata. MLflow requires Postgres for backend store. MinIO is shared to reduce container count (saves ~1GB RAM and 1 container). Local MinIO is the recommended approach for both Langfuse and MLflow local development (per official docs from both projects).

**Alternatives considered:**
- Shared Postgres with separate schemas: Simpler infra, but risks cross-service schema conflicts and connection pool contention. Rejected for isolation.
- Separate MinIO instances: More isolation but adds containers and RAM. Rejected for resource efficiency.
- SQLite for MLflow: Not suitable for team use or production. Rejected.
- Cloud S3: Not applicable — local development only. Cloud deployment is a future concern.

### D5: Langfuse integration — dual path (OTel Collector + optional @observe())

**Decision:** Primary integration via OTel Collector routing (existing spans → Collector → Langfuse). Optional secondary integration via Langfuse @observe() decorator on BaseAgent.run() when richer Langfuse-native features are needed (session tracking, prompt/playground).

**Rationale:** BaseAgent.run() already emits OTel spans via `tracer.start_as_current_span(OP_INVOKE_AGENT)` at `agent.py:210`. The OTel Collector can route these existing spans to Langfuse without any code changes to BaseAgent. This is the lowest-risk path. For teams needing Langfuse-native features (session grouping, prompt management), the @observe() decorator can be enabled via config flag. This avoids forced duplication while providing an opt-in upgrade path.

**Alternatives considered:**
- Use only @observe(): Creates duplicate traces (one from OTel, one from Langfuse SDK). Rejected for duplication.
- Use only OTel → Langfuse OTLP ingest: Misses Langfuse-specific features (session tracking, prompt/playground integration). Rejected for feature gap — but acceptable as default.
- Use both by default: Duplicate traces with no way to distinguish. Rejected for confusion.

### D6: MLflow autolog() for Pydantic AI

**Decision:** Enable `mlflow.pydantic_ai.autolog()` in BaseAgent initialization. This automatically traces agent runs, LLM calls, and tool invocations to the MLflow tracking server.

**Rationale:** MLflow's Pydantic AI autolog captures the same data as Langfuse but in MLflow's experiment tracking format. This enables experiment comparison, parameter diffing, and the full MLflow evaluation pipeline. The overhead is minimal (async, batched).

**Alternatives considered:**
- Manual logging only: More control, but more code and maintenance. Rejected for autolog maturity.
- Skip MLflow tracing, use only experiment logging: Misses trace-level data in MLflow UI. Rejected for completeness.

### D7: Scorer framework in agent_core.observability.scorers

**Decision:** Create a dedicated scorer subpackage with reusable code evaluators and LLM-as-Judge evaluators. Scorers work with both Langfuse (via langfuse.score()) and MLflow (via mlflow.genai.evaluate()).

**Rationale:** Centralizes evaluation logic. Code evaluators (latency, cost, tool_usage, regression) are deterministic and cheap. LLM-as-Judge evaluators (correctness, relevance, plan_adherence) use LLM calls for semantic quality assessment. Having them in one place avoids duplication.

**Alternatives considered:**
- Evaluate only via MLflow scorers: Misses Langfuse's real-time score analytics. Rejected.
- Evaluate only via Langfuse scores: Misses MLflow's experiment comparison and prompt optimization. Rejected.
- Inline evaluation in hooks: Scatters evaluation logic across hook packs. Rejected for maintainability.

## Risks / Trade-offs

- **[OTel coverage gaps]** Currently, only `BaseAgent.run()` emits an OTel span (agent.py:210). LLM calls in `BifrostGateway.complete()` (gateway.py:243) and tool execution in `ToolRegistry.execute()` (registry.py:123) have NO OTel spans. Langfuse via Collector would only see the outer agent span, missing LLM and tool details. → Mitigation: Add OTel spans to gateway and registry before deploying Langfuse integration. This is a prerequisite task (tasks 3.4, 3.5).
- **[Hook double-fire]** `HookPoint.RUN` BEFORE/AFTER hooks fire twice per run: once from `BaseAgent.run()` directly (agent.py:234,337) and once from `HookAdapter` bridging pydantic-ai (hooks.py). Tool and model hooks fire once. → Mitigation: Langfuse/MLflow hook packs use a deduplication flag (`_langfuse_scores_recorded`) in context dict to prevent double-recording.
- **[Operational complexity]** ~10 new Docker containers (Langfuse 6 + MLflow 2 + OTel Collector 1, MinIO shared) is significant for a small team. Total stack: ~13 containers. → Mitigation: Document resource requirements clearly. Consider shared Postgres for Langfuse + MLflow in dev environments. Monitor container health via agent-core health checks. MinIO is shared to reduce count.
- **[ClickHouse resource usage]** ClickHouse needs 4GB RAM for trace aggregation (per Langfuse docs). → Mitigation: Set Docker memory limit to 4GB. Scale up as trace volume grows. Use Docker resource limits.
- **[MLflow SDK dependency weight]** MLflow pulls in many transitive dependencies. → Mitigation: Use `mlflow[genai]` minimal install. Pin versions. Monitor package size.
- **[Dual tracing overhead]** Both OTel Collector routing and MLflow autolog() trace the same agent runs. → Mitigation: Both are async and batched. Overhead is negligible vs LLM latency. Different purposes (observability vs experiment tracking) justify duplication.
- **[Migration risk]** Dropping eval_metrics table could lose historical data. → Mitigation: Dual-write phase (2-4 weeks). Export existing data to MLflow before dropping. Keep Postgres backup.
- **[Langfuse v3 maturity]** v3 with ClickHouse is relatively new (2025). → Mitigation: MIT license, active community, ClickHouse acquisition provides long-term support. Docker Compose is officially supported.

## Migration Plan

1. **Phase 1 — Infrastructure**: Add Docker Compose services (Langfuse, MLflow, OTel Collector). Validate all services healthy. No code changes.
2. **Phase 2 — Langfuse**: Add observability.langfuse_client, wrap BaseAgent.run() with @observe(), route OTel via Collector. Verify traces appear in Langfuse UI.
3. **Phase 3 — MLflow**: Add observability.mlflow_client, enable autolog(), log experiments. Verify experiments appear in MLflow UI.
4. **Phase 4 — Scorers**: Add scorer framework. Run evaluations against existing agent runs. Compare with current regressions() output.
5. **Phase 5 — Migration**: Dual-write to Postgres + Langfuse + MLflow. Validate query parity. Drop eval_metrics table. Deprecate evaluation/store.py.
6. **Phase 6 — CLI + Polish**: Add observability status, eval commands. Update config validation. Documentation.

**Rollback:** Each phase is independently reversible. Phase 1-3: remove Docker services and revert code. Phase 5: restore eval_metrics table from backup before dropping.

## Open Questions

1. **Langfuse Postgres sharing**: Can Langfuse and MLflow share a Postgres instance with separate databases, or do they need separate Postgres containers? (Langfuse docs suggest separate, but shared may work for small deployments.)
2. **MinIO vs RustFS**: MLflow's official Docker Compose uses RustFS (S3-compatible, Rust). MinIO is more established. Which to use? (Both are S3-compatible, either works.)
3. **Prompt Registry scope**: Should MLflow prompt registry manage ALL agent prompts (system prompts, tool descriptions, skill instructions) or only system prompts? (Scope creep risk.)
4. **Langfuse session vs trace**: For multi-turn agent conversations, should each turn be a separate trace or one session with multiple traces? (Affects cost tracking granularity.)
