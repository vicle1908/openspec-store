## 1. Module Setup

- [x] 1.1 Create `agent_core/evaluation/__init__.py` module
- [x] 1.2 Define `EvalRecord` Pydantic model in `agent_core/evaluation/types.py` with operational, quality, and behavioral fields
- [x] 1.3 Create `agent_core/evaluation/store.py` with `EvalMetrics` class

## 2. Database

- [x] 2.1 Create migration for `agent_memory.eval_metrics` table with all EvalRecord columns
- [x] 2.2 Add indexes on `agent_name`, `created_at`, and `success` columns
- [x] 2.3 Verify migration runs cleanly on existing database

## 3. Store Implementation

- [x] 3.1 Implement `EvalMetrics.record()` method for inserting EvalRecord instances
- [x] 3.2 Implement `EvalMetrics.query()` method with time-range filtering and aggregation
- [x] 3.3 Implement `EvalMetrics.compare()` method for baseline vs current comparison
- [x] 3.4 Implement `EvalMetrics.regressions()` method with configurable thresholds
- [x] 3.5 Implement p50/p95/p99 percentile calculations using SQL PERCENTILE_CONT

## 4. Auto-Recording Integration

- [x] 4.1 Wire `EvalMetrics.record()` into `AgentRuntime.run()` completion path
- [x] 4.2 Capture latency, cost, token usage, iteration count from AgentResult
- [x] 4.3 Capture tool success/failure rates from run context
- [x] 4.4 Add opt-out flag `record_metrics=False` to AgentRuntime constructor

## 5. CLI

- [x] 5.1 Add `agent-core eval report --agent <name> --since <duration>` command
- [x] 5.2 Display summary: total runs, success rate, p50/p95 latency, total cost
- [x] 5.3 Add regression flags for metrics exceeding thresholds

## 6. Tests

- [x] 6.1 Create `tests/evaluation/__init__.py` and `tests/evaluation/test_store.py`
- [x] 6.2 Test `EvalMetrics.record()` inserts correctly
- [x] 6.3 Test `EvalMetrics.query()` with time-range filters
- [x] 6.4 Test `EvalMetrics.compare()` calculates deltas correctly
- [x] 6.5 Test `EvalMetrics.regressions()` detects threshold violations
- [x] 6.6 Test auto-recording in AgentRuntime.run()
- [x] 6.7 Run `pytest tests/evaluation/ -x`

## 7. Validation

- [x] 7.1 Run `mypy agent_core/evaluation/ --strict`
- [x] 7.2 Run `ruff check agent_core/evaluation/ && ruff format agent_core/evaluation/`
- [x] 7.3 Run full test suite `pytest tests/ -x`
