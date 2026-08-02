# Scorer Framework

**Capability:** scorer-framework
**Status:** Implemented (agent-core observability module)
**Date:** 2026-07-25

## Purpose

Evaluation scorer framework for agent quality assessment using pydantic-evals built-in evaluators + custom CostScorer and RegressionScorer. Integrates with Langfuse (via OTel traces) and MLflow (via experiment logging).

## Requirements

### Requirement: pydantic-evals integration
The system SHALL use pydantic-evals v2.18.0 (`pydantic-evals>=2.18.0,<3`) as the core evaluation framework. The `Dataset`, `Case`, `Evaluator`, `EvaluatorContext`, and `EvaluationReport` classes from pydantic-evals SHALL be the primary API for defining and running evaluations. Custom evaluators SHALL extend `Evaluator` and implement `evaluate(ctx: EvaluatorContext)` which receives name, inputs, metadata, expected_output, output, duration, metrics, attributes, and span_tree.

#### Scenario: Dataset with cases and evaluators
- **WHEN** a `Dataset` is created with `Case` objects and built-in evaluators
- **THEN** `dataset.evaluate_sync(task_function)` runs all cases and returns an `EvaluationReport`

#### Scenario: pydantic-evals traces sent to Langfuse
- **WHEN** `logfire.configure()` or OTel is configured before evaluation
- **THEN** evaluation traces appear in Langfuse UI via OTLP ingestion

### Requirement: Built-in evaluators for agent quality
The system SHALL use pydantic-evals built-in evaluators for deterministic and agent-specific checks.

**Case-level evaluators (13 available):**

| Evaluator | Purpose | Agent Relevance |
|-----------|---------|-----------------|
| `MaxDuration(seconds=...)` | Performance threshold | Latency SLA |
| `HasMatchingSpan(query={...})` | OTel span behavioral check | Tool call verification |
| `ToolCorrectness(tools=[...])` | Required tool multiset coverage | Tool usage validation |
| `MaxToolCalls(max_calls=N)` | Tool-call budget enforcement | Cost/efficiency control |
| `MaxModelRequests(max_requests=N)` | Model request budget | Token cost control |
| `ArgumentCorrectness(tool, args)` | Tool argument validation | Correct tool usage |
| `TrajectoryMatch(expected=[...])` | Tool-call sequence quality | Plan adherence |
| `EqualsExpected()` | Exact output match | Correctness check |
| `Contains(value=...)` | Substring/list/dict check | Required content |
| `IsInstance(type_name=...)` | Type validation | Format validation |
| `Equals(value=...)` | Specific value match | Sentinel checks |
| `LLMJudge(rubric=...)` | Subjective quality (LLM) | Relevance, tone, quality |
| `GEval(criteria=..., evaluation_steps=[...])` | Chain-of-thought scoring | Complex quality assessment |

**Report-level evaluators (4 available):**

| Evaluator | Purpose |
|-----------|---------|
| `ConfusionMatrixEvaluator` | Classification confusion matrix |
| `PrecisionRecallEvaluator` | PR curve with AUC |
| `ROCAUCEvaluator` | ROC curve and AUC |
| `KolmogorovSmirnovEvaluator` | KS plot and statistic |

#### Scenario: MaxDuration evaluator
- **WHEN** `MaxDuration(seconds=2.0)` evaluates a trace with `duration=1.5s`
- **THEN** it returns pass (True)

#### Scenario: HasMatchingSpan evaluator
- **WHEN** `HasMatchingSpan(query={'name_contains': 'search_database'})` evaluates a trace
- **THEN** it returns pass (True) if the span exists

#### Scenario: ToolCorrectness evaluator
- **WHEN** `ToolCorrectness(tools=['shell_execute', 'git_diff'])` evaluates a trace
- **THEN** it returns pass (True) if both tools were called

#### Scenario: MaxToolCalls evaluator
- **WHEN** `MaxToolCalls(max_calls=5)` evaluates a trace with 3 tool calls
- **THEN** it returns pass (True)

#### Scenario: TrajectoryMatch evaluator
- **WHEN** `TrajectoryMatch(expected=['plan', 'search', 'execute'])` evaluates a trace
- **THEN** it returns pass (True) if the tool-call sequence matches

#### Scenario: LLMJudge evaluator
- **WHEN** `LLMJudge(rubric='Response is relevant to the query', include_input=True)` evaluates a trace
- **THEN** it returns a boolean score with reasoning from the LLM

### Requirement: LLM-as-Judge evaluators
The system SHALL use pydantic-evals `LLMJudge` for subjective quality assessment. The `LLMJudge` evaluator sends a rubric to an LLM and returns pass/fail with reasoning.

#### Scenario: Correctness judge
- **WHEN** `LLMJudge(rubric='Response is factually correct')` evaluates a trace
- **THEN** it returns a boolean score with reasoning

#### Scenario: Relevance judge
- **WHEN** `LLMJudge(rubric='Response is relevant to the query', include_input=True)` evaluates a trace
- **THEN** it returns a boolean score with reasoning

### Requirement: Custom CostScorer
The system SHALL provide a `CostScorer` custom evaluator (extending pydantic-evals `Evaluator` with `@dataclass`) that scores cost-per-token efficiency. The evaluator SHALL read `cost_usd` and `tokens_total` from `ctx.metrics` or `ctx.attributes` and return a numeric score (0-1). This evaluator has no pydantic-evals equivalent.

#### Scenario: Cost efficiency scoring
- **WHEN** `CostScorer()` evaluates a trace with `cost_usd=0.05` and `tokens_total=2000`
- **THEN** it returns a numeric score (0-1) based on cost-per-token efficiency

### Requirement: Custom RegressionScorer
The system SHALL provide a `RegressionScorer` custom evaluator (extending pydantic-evals `Evaluator` with `@dataclass`) that compares current metrics against configurable thresholds. The evaluator SHALL accept `baseline_latency_ms`, `baseline_success_rate`, `latency_threshold`, and `success_threshold` parameters and read latency/cost/success metrics from `ctx.metrics` or `ctx.attributes`. Returns dict with `passed` (bool) and `rationale` (str). This evaluator has no pydantic-evals equivalent.

#### Scenario: Regression detected
- **WHEN** `RegressionScorer(baseline_latency_ms=5000)` evaluates a run with latency_ms=7000 (40% above baseline)
- **THEN** it returns `{"passed": False, "rationale": "latency +40%"}`

#### Scenario: No regression
- **WHEN** `RegressionScorer(baseline_latency_ms=5000)` evaluates a run with latency_ms=3000
- **THEN** it returns `{"passed": True, "rationale": "within baseline"}`

### Requirement: MLflow integration
Evaluation results from pydantic-evals SHALL be logged to MLflow via the existing MLflowClient. Summary metrics (total cases, pass rate, average scores) SHALL be logged as MLflow experiment metrics.

#### Scenario: Eval results logged to MLflow
- **WHEN** `run_evaluation()` completes with `targets=["mlflow"]`
- **THEN** summary metrics are logged to MLflow via `MLflowClient.log_metrics()`

### Requirement: Evaluation runner
The system SHALL provide `run_evaluation(dataset, task_function, targets)` that runs a pydantic-evals Dataset evaluation and optionally records results to specified backends (langfuse/mlflow).

#### Scenario: Full evaluation
- **WHEN** `run_evaluation(dataset=my_dataset, task_function=my_agent, targets=["langfuse", "mlflow"])` is called
- **THEN** evaluation runs, traces go to Langfuse via OTel, and summary metrics go to MLflow
