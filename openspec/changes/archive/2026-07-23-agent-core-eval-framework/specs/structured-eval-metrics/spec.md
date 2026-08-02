## ADDED Requirements

### Requirement: EvalRecord structured model
The system SHALL define `EvalRecord` as a Pydantic model with typed fields for operational, quality, and behavioral metrics.

#### Scenario: EvalRecord has operational fields
- **WHEN** an `EvalRecord` is created
- **THEN** it SHALL include:
  - `run_id: str` — unique run identifier
  - `agent_name: str` — agent that performed the run
  - `latency_ms: float` — total wall-clock time
  - `cost_usd: float | None` — total cost (if available)
  - `tokens_prompt: int` — input tokens consumed
  - `tokens_completion: int` — output tokens generated
  - `iterations: int` — number of model/tool iterations

#### Scenario: EvalRecord has quality fields
- **WHEN** an `EvalRecord` is created
- **THEN** it SHALL include:
  - `success: bool` — whether the run completed successfully
  - `accuracy_score: float | None` — optional accuracy rating (0.0 to 1.0)
  - `tool_success_rate: float | None` — percentage of tool calls that succeeded

#### Scenario: EvalRecord has behavioral fields
- **WHEN** an `EvalRecord` is created
- **THEN** it SHALL include:
  - `tools_used: list[str]` — names of tools invoked
  - `tools_succeeded: list[str]` — names of tools that succeeded
  - `tools_failed: list[str]` — names of tools that failed
  - `retry_count: int` — number of retries
  - `human_interventions: int` — number of approval gate interruptions

#### Scenario: EvalRecord has metadata fields
- **WHEN** an `EvalRecord` is created
- **THEN** it SHALL include:
  - `model: str` — LLM model used
  - `skill: str | None` — skill that was active
  - `task_summary: str` — brief description of the task
  - `created_at: datetime` — timestamp of the record
  - `custom: dict[str, Any]` — arbitrary metadata for extensibility

### Requirement: Eval metrics storage
The system SHALL persist `EvalRecord` instances in an `agent_memory.eval_metrics` Postgres table.

#### Scenario: Record is stored
- **WHEN** `EvalMetrics.record(eval_record)` is called
- **THEN** the record SHALL be inserted into `agent_memory.eval_metrics` with all fields persisted as typed columns

#### Scenario: Table schema
- **WHEN** the migration runs
- **THEN** `agent_memory.eval_metrics` SHALL exist with columns matching `EvalRecord` fields:
  - `run_id TEXT PRIMARY KEY`
  - `agent_name TEXT NOT NULL`
  - `latency_ms DOUBLE PRECISION NOT NULL`
  - `cost_usd DOUBLE PRECISION`
  - `tokens_prompt INTEGER NOT NULL DEFAULT 0`
  - `tokens_completion INTEGER NOT NULL DEFAULT 0`
  - `iterations INTEGER NOT NULL DEFAULT 0`
  - `success BOOLEAN NOT NULL DEFAULT FALSE`
  - `accuracy_score DOUBLE PRECISION`
  - `tool_success_rate DOUBLE PRECISION`
  - `tools_used TEXT[] DEFAULT '{}'"
  - `tools_succeeded TEXT[] DEFAULT '{}'"
  - `tools_failed TEXT[] DEFAULT '{}'"
  - `retry_count INTEGER NOT NULL DEFAULT 0`
  - `human_interventions INTEGER NOT NULL DEFAULT 0`
  - `model TEXT NOT NULL DEFAULT ''"
  - `skill TEXT"
  - `task_summary TEXT NOT NULL DEFAULT ''"
  - `custom JSONB DEFAULT '{}'"
  - `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"

#### Scenario: Table has proper indexes
- **WHEN** the migration runs
- **THEN** indexes SHALL exist on:
  - `agent_name` (for agent-specific queries)
  - `created_at` (for time-range queries)
  - `success` (for filtering by outcome)

### Requirement: Time-range query API
The system SHALL provide a `query()` method that retrieves eval records by agent name and time range.

#### Scenario: Query by agent and time range
- **WHEN** `EvalMetrics.query(agent_name="my-agent", since=one_day_ago, until=now)` is called
- **THEN** all matching `EvalRecord` instances SHALL be returned ordered by `created_at` DESC

#### Scenario: Query returns percentile aggregates
- **WHEN** `EvalMetrics.query(agent_name="my-agent", since=one_day_ago, aggregate=True)` is called
- **THEN** the result SHALL include:
  - `total_runs: int` — count of matching runs
  - `success_rate: float` — percentage of successful runs
  - `p50_latency_ms: float` — 50th percentile latency
  - `p95_latency_ms: float` — 95th percentile latency
  - `p99_latency_ms: float` — 99th percentile latency
  - `mean_cost_usd: float | None` — average cost
  - `total_tokens: int` — total tokens consumed

#### Scenario: Percentile calculation method
- **WHEN** percentiles are calculated
- **THEN** the system SHALL use SQL `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms)` for p50
- **AND** `PERCENTILE_CONT(0.95)` for p95 and `PERCENTILE_CONT(0.99)` for p99

### Requirement: Comparison API
The system SHALL provide a `compare()` method that contrasts two sets of eval records.

#### Scenario: Compare two time ranges
- **WHEN** `EvalMetrics.compare(agent_name="my-agent", baseline_range=last_week, current_range=this_week)` is called
- **THEN** the result SHALL include delta metrics for:
  - `latency_ms_delta: float` — change in p95 latency (current - baseline)
  - `cost_usd_delta: float | None` — change in mean cost
  - `success_rate_delta: float` — change in success rate
  - `tool_success_rate_delta: float | None` — change in tool success rate
  - `regression_detected: bool` — whether any metric degraded beyond threshold

### Requirement: Regression detection
The system SHALL provide a `regressions()` method that detects statistically significant degradation.

#### Scenario: Detect latency regression
- **WHEN** `EvalMetrics.regressions(agent_name="my-agent", metric="latency_ms", threshold=0.2)` is called
- **THEN** the result SHALL list any metrics where the current p95 exceeds the baseline p95 by more than the threshold (20%)
- **AND** each regression SHALL include `metric_name`, `baseline_value`, `current_value`, `delta_pct`

#### Scenario: No regression detected
- **WHEN** all metrics are within threshold
- **THEN** an empty list SHALL be returned

### Requirement: Auto-recording on agent runs
The system SHALL automatically record an `EvalRecord` after each `AgentRuntime.run()` completion.

#### Scenario: Successful run recorded
- **WHEN** `AgentRuntime.run()` completes with `completed=True`
- **THEN** an `EvalRecord` with `success=True` and actual timing/cost/token data SHALL be stored

#### Scenario: Failed run recorded
- **WHEN** `AgentRuntime.run()` completes with `completed=False`
- **THEN** an `EvalRecord` with `success=False` and the failure reason in `task_summary` SHALL be stored

#### Scenario: Opt-out flag
- **WHEN** `AgentRuntime(..., record_metrics=False)` is constructed
- **THEN** auto-recording SHALL be disabled for that runtime instance

### Requirement: CLI eval report command
The system SHALL provide `agent-core eval report --agent <name> --since <duration>` CLI command.

#### Scenario: Generate report
- **WHEN** `agent-core eval report --agent my-agent --since 7d` is executed
- **THEN** a summary SHALL be printed with:
  - Total runs in period
  - Success rate (%)
  - p50 / p95 / p99 latency
  - Total cost
  - Regression flags for metrics exceeding thresholds

#### Scenario: JSON output
- **WHEN** `agent-core eval report --agent my-agent --since 7d --json` is executed
- **THEN** the report SHALL be output as structured JSON
