## Context

The `FeedbackStore` in `agent_core/memory/postgres.py` captures episodic run data (run_id, agent_name, duration, cost, completion status) but lacks structured metrics. There are no latency percentiles, no accuracy scores, no tool success rates, and no regression detection. The `FeedbackEntry` dataclass has a flexible `signals: dict[str, Any]` field but no schema enforcement.

## Goals / Non-Goals

**Goals:**
- Structured `EvalRecord` model with typed operational, quality, and behavioral fields
- Query API with time-range filtering, percentile calculations, and aggregation
- Comparison API for run-over-run and model-vs-model analysis
- Regression detection with configurable thresholds
- Auto-recording on every `AgentRuntime.run()` call

**Non-Goals:**
- Replacing LangSmith/Logfire (eval framework complements, not replaces)
- Real-time dashboards (CLI + API only in v1)
- Evaluation scoring of output quality (requires human or LLM judge — future)
- Cross-agent comparison (agent-specific in v1)

## Decisions

### Decision 1: New table, not extending FeedbackStore

**Choice:** Create `agent_memory.eval_metrics` as a separate table

**Rationale:**
- `FeedbackStore` is append-only episodic records — different access pattern
- `eval_metrics` needs indexed columns for time-range queries and aggregation
- Separation allows independent schema evolution
- FeedbackStore can reference eval_metrics via `run_id` FK if needed

### Decision 2: Auto-record in AgentRuntime, not in node handlers

**Choice:** Wire metrics capture into `AgentRuntime.run()` completion path

**Rationale:**
- Every agent run goes through `AgentRuntime.run()` — single capture point
- Node handlers are user-defined — can't guarantee they record metrics
- AgentRuntime already has access to usage, timing, and result data

### Decision 3: Postgres-native aggregation (not external analytics)

**Choice:** Use SQL window functions for percentiles, not a separate analytics DB

**Rationale:**
- Already have Postgres with `agent_memory` schema
- SQL `PERCENTILE_CONT` gives p50/p95/p99 natively
- No new infrastructure dependency
- Can add materialized views later for dashboards

## Risks / Trade-offs

**[Risk] Performance overhead on every run** → Recording metrics adds one INSERT per run. Mitigation: Async INSERT (fire-and-forget), batch inserts if needed.

**[Risk] Schema drift between EvalRecord and FeedbackEntry** → They track similar but different data. Mitigation: EvalRecord extends FeedbackEntry conceptually but is a separate model — no inheritance needed.

**[Risk] Migration complexity** → New table + index. Mitigation: Simple CREATE TABLE migration, no data migration needed.

## Migration Plan

1. Create `agent_core/evaluation/__init__.py`, `types.py`, `store.py`, `cli.py`
2. Define `EvalRecord` Pydantic model in `types.py`
3. Create migration for `eval_metrics` table with indexes
4. Implement `EvalMetrics` store with query/compare/regressions methods
5. Wire auto-recording into `AgentRuntime.run()` completion path
6. Add `agent-core eval report` CLI command
7. Add tests in `tests/evaluation/`

## Open Questions

- Should we add an `accuracy_score` field that accepts float 0-1, or leave it as optional `signals` dict? (Recommend: float field for queryability)
- Should eval metrics be opt-in per agent or automatic for all? (Recommend: automatic, with opt-out flag)
