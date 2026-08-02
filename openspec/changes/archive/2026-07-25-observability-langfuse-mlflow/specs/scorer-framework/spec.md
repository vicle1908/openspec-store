## ADDED Requirements

### Requirement: Code evaluator scorers
The system SHALL provide deterministic code-based evaluators in `agent_core.observability.scorers` that evaluate agent runs without LLM calls. Scorers SHALL be usable with both Langfuse (via `langfuse.score()`) and MLflow (via `@mlflow.genai.scorer`).

#### Scenario: Latency scorer
- **WHEN** `LatencyScorer()` evaluates a trace with `latency_ms=5000`
- **THEN** it returns a numeric score (0-1) based on configured thresholds (e.g., <1s=1.0, <5s=0.8, <10s=0.5, >10s=0.2)

#### Scenario: Cost efficiency scorer
- **WHEN** `CostScorer()` evaluates a trace with `cost_usd=0.05` and `tokens_total=2000`
- **THEN** it returns a numeric score based on cost-per-token efficiency

#### Scenario: Tool usage scorer
- **WHEN** `ToolUsageScorer()` evaluates a trace with `tools_used=["shell_execute", "git_diff"]` and `tools_succeeded=["shell_execute"]`
- **THEN** it returns a numeric score (0.5) reflecting 50% tool success rate

### Requirement: Regression detection scorer
The system SHALL provide a `RegressionScorer` that compares current agent run metrics against a baseline window and detects regressions in latency, cost, or success rate.

#### Scenario: Latency regression detected
- **WHEN** `RegressionScorer(baseline_window="7d")` evaluates a run with p95 latency 30% above baseline
- **THEN** it returns a boolean score `false` (regression detected) with comment detailing the delta

#### Scenario: No regression
- **WHEN** `RegressionScorer(baseline_window="7d")` evaluates a run within normal baseline range
- **THEN** it returns a boolean score `true` (no regression)

### Requirement: LLM-as-Judge evaluators
The system SHALL provide LLM-as-Judge evaluators that use a separate LLM to assess agent output quality. Evaluators SHALL support configurable model (OpenAI, Anthropic, or any LiteLLM-compatible provider).

#### Scenario: Correctness judge
- **WHEN** `CorrectnessJudge(model="openai:gpt-4o")` evaluates a trace with input "What is 2+2?" and output "4"
- **THEN** it returns a numeric score (0-1) indicating factual correctness

#### Scenario: Relevance judge
- **WHEN** `RelevanceJudge(model="openai:gpt-4o")` evaluates a trace with input "Review auth.py" and output "The code uses MD5 for password hashing"
- **THEN** it returns a numeric score (0-1) indicating response relevance to the query

#### Scenario: Plan adherence judge
- **WHEN** `PlanAdherenceJudge(model="openai:gpt-4o")` evaluates an agent trace with a planning step and execution steps
- **THEN** it returns a numeric score (0-1) indicating whether execution followed the plan

### Requirement: Scorer integration with Langfuse
The system SHALL record scorer results as Langfuse scores attached to the evaluated trace. Each score SHALL have a name, numeric/boolean value, optional comment, and data type.

#### Scenario: Score recorded on Langfuse trace
- **WHEN** `LatencyScorer().evaluate_langfuse(trace_id="abc-123", trace_data={...})` is called
- **THEN** a Langfuse score `latency_score=0.8` is attached to trace `abc-123`

### Requirement: Scorer integration with MLflow
The system SHALL expose scorers as `@mlflow.genai.scorer` decorated functions compatible with `mlflow.genai.evaluate()`.

#### Scenario: Scorer used in MLflow evaluation
- **WHEN** `mlflow.genai.evaluate(data=dataset, predict_fn=agent.run, scorers=[latency_scorer])` is called
- **THEN** the scorer is executed against each trace and results are logged to MLflow

### Requirement: Composite evaluation runner
The system SHALL provide a `run_evaluation()` function that orchestrates code evaluators, LLM-as-Judge evaluators, and optional human annotation across a set of traces, recording results to both Langfuse and MLflow.

#### Scenario: Full evaluation run
- **WHEN** `run_evaluation(traces=[...], code_scorers=[LatencyScorer()], judge_scorers=[CorrectnessJudge()], targets=["langfuse", "mlflow"])` is called
- **THEN** all scorers are executed, results are recorded to both backends, and a summary report is returned
